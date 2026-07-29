"""Tests for the dependency-floor audit (scripts/audit_dependency_floors.py).

Scope is deliberately narrow. The OSV lookups are CI's job, not the unit suite's:
they need the network and their answers change as advisories are published. What
is worth testing here is the parsing that decides *which* floors get audited — a
requirement this misreads is a requirement that silently escapes the audit — plus
guards on the declared floors themselves.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

try:  # tomllib is stdlib from 3.11; tomli is the dev-extra backport for 3.10.
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - only taken on Python 3.10
    import tomli as tomllib

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "audit_dependency_floors.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("audit_dependency_floors", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_dependency_floors"] = module
    spec.loader.exec_module(module)
    return module


audit_mod = _load_module()


def _pyproject() -> dict:
    with open(REPO_ROOT / "pyproject.toml", "rb") as handle:
        return tomllib.load(handle)


class TestParseRequirement:
    """A misparse means a requirement escapes the audit, so parsing is the risk."""

    @pytest.mark.parametrize(
        ("spec", "name", "floor"),
        [
            ("requests>=2.33.0", "requests", "2.33.0"),
            ("trafilatura>=2.0,<3", "trafilatura", "2.0"),  # floor beside a ceiling
            ("confusable_homoglyphs>=3.3", "confusable-homoglyphs", "3.3"),  # PEP 503
            ("requests[socks]>=2.33.0", "requests", "2.33.0"),  # extras bracket
            ('tomli>=2.0; python_version < "3.11"', "tomli", "2.0"),  # env marker
            ("pytest-cov", "pytest-cov", None),  # no floor to audit
            ("somepkg<3", "somepkg", None),  # ceiling only is not a floor
        ],
    )
    def test_extracts_name_and_floor(self, spec: str, name: str, floor: str | None) -> None:
        req = audit_mod.parse_requirement(spec, "test")
        assert req is not None
        assert (req.name, req.floor) == (name, floor)


class TestVersionOrdering:
    def test_orders_numerically_not_lexically(self) -> None:
        """String comparison would put 1.0.10 below 1.0.9 and pick a vulnerable floor."""
        versions = ["1.0.9", "1.0.10", "1.0.6"]
        assert sorted(versions, key=audit_mod._version_key) == ["1.0.6", "1.0.9", "1.0.10"]


class TestCollectRequirements:
    def test_collects_from_every_table(self) -> None:
        """A table missed here is a table that never gets audited."""
        pyproject = {
            "build-system": {"requires": ["setuptools>=83.0.0", "wheel"]},
            "project": {
                "dependencies": ["requests>=2.33.0"],
                "optional-dependencies": {
                    "anchor": ["cryptography>=48.0.1"],
                    "dev": ["pytest>=9.0.3"],
                },
            },
        }
        origins = {r.name: r.origin for r in audit_mod.collect_requirements(pyproject)}
        assert origins == {
            "setuptools": "build-system.requires",
            "wheel": "build-system.requires",
            "requests": "project.dependencies",
            "cryptography": "optional-dependencies.anchor",
            "pytest": "optional-dependencies.dev",
        }


class TestDeclaredFloors:
    """Guards on pyproject.toml itself. No network required."""

    def test_rfc3161_client_floor_excludes_cve_2026_33753(self) -> None:
        """Every declaration must exclude the TSA-impersonation bypass (<1.0.6).

        freeTSA is the default anchoring backend and the advisory's worked
        example, so a lower floor would undermine what `verify` guarantees.
        """
        declared = [
            r.floor
            for r in audit_mod.collect_requirements(_pyproject())
            if r.name == "rfc3161-client" and r.floor
        ]
        assert declared, "rfc3161-client must declare a floor"
        for floor in declared:
            assert audit_mod._version_key(floor) >= audit_mod._version_key("1.0.6")

    def test_every_runtime_dependency_declares_a_floor(self) -> None:
        for req in audit_mod.collect_requirements(_pyproject()):
            if req.origin == "project.dependencies":
                assert req.floor is not None, f"{req.name} has no lower bound to audit"

    def test_floorless_requirements_are_all_allowlisted(self) -> None:
        """Adding a floor-free requirement should fail here, not silently skip the audit."""
        floorless = {r.name for r in audit_mod.collect_requirements(_pyproject()) if not r.floor}
        assert floorless <= audit_mod.NO_FLOOR_EXPECTED
