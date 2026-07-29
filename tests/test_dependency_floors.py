"""Tests for the dependency-floor audit (scripts/audit_dependency_floors.py).

Only the network-free logic is exercised here: requirement parsing, version
ordering, and the declared floors in pyproject.toml itself. The OSV lookups are
CI's job, not the unit suite's — they need the network and their answers change
as advisories are published.
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


class TestParseRequirement:
    @pytest.mark.parametrize(
        ("spec", "name", "floor"),
        [
            ("requests>=2.33.0", "requests", "2.33.0"),
            ("trafilatura>=2.0,<3", "trafilatura", "2.0"),
            ("rfc3161-client>=1.0.6", "rfc3161-client", "1.0.6"),
            ("cryptography>=48.0.1", "cryptography", "48.0.1"),
            ("pytest-cov", "pytest-cov", None),
            ("ruff", "ruff", None),
            ("types-PyYAML", "types-pyyaml", None),
            ("confusable_homoglyphs>=3.3", "confusable-homoglyphs", "3.3"),
            ("setuptools == 83.0.0", "setuptools", "83.0.0"),
        ],
    )
    def test_extracts_name_and_floor(self, spec: str, name: str, floor: str | None) -> None:
        req = audit_mod.parse_requirement(spec, "test")
        assert req is not None
        assert req.name == name
        assert req.floor == floor

    def test_strips_environment_marker(self) -> None:
        req = audit_mod.parse_requirement('tomli>=2.0; python_version < "3.11"', "test")
        assert req is not None
        assert req.name == "tomli"
        assert req.floor == "2.0"

    def test_handles_extras_bracket(self) -> None:
        req = audit_mod.parse_requirement("requests[socks]>=2.33.0", "test")
        assert req is not None
        assert req.name == "requests"
        assert req.floor == "2.33.0"

    def test_upper_bound_only_has_no_floor(self) -> None:
        req = audit_mod.parse_requirement("somepkg<3", "test")
        assert req is not None
        assert req.floor is None

    def test_empty_spec_is_skipped(self) -> None:
        assert audit_mod.parse_requirement("   ", "test") is None


class TestVersionKey:
    def test_orders_numerically_not_lexically(self) -> None:
        # The bug this guards: "1.0.10" sorts below "1.0.9" under string comparison.
        versions = ["1.0.9", "1.0.10", "1.0.6"]
        assert sorted(versions, key=audit_mod._version_key) == ["1.0.6", "1.0.9", "1.0.10"]

    def test_shorter_version_sorts_below_longer(self) -> None:
        assert audit_mod._version_key("1.0") < audit_mod._version_key("1.0.1")

    def test_tolerates_non_numeric_segments(self) -> None:
        assert audit_mod._version_key("2.0.0rc1") == (2, 0, 1)


class TestCollectRequirements:
    def test_collects_from_every_table(self) -> None:
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
        reqs = audit_mod.collect_requirements(pyproject)
        by_name = {r.name: r for r in reqs}
        assert by_name["setuptools"].origin == "build-system.requires"
        assert by_name["requests"].origin == "project.dependencies"
        assert by_name["cryptography"].origin == "optional-dependencies.anchor"
        assert by_name["pytest"].origin == "optional-dependencies.dev"

    def test_missing_tables_do_not_raise(self) -> None:
        assert audit_mod.collect_requirements({}) == []


class TestDeclaredFloors:
    """Regression guards on pyproject.toml itself. No network required."""

    @staticmethod
    def _floors() -> dict[str, list[str]]:
        with open(REPO_ROOT / "pyproject.toml", "rb") as handle:
            pyproject = tomllib.load(handle)
        floors: dict[str, list[str]] = {}
        for req in audit_mod.collect_requirements(pyproject):
            if req.floor:
                floors.setdefault(req.name, []).append(req.floor)
        return floors

    def test_rfc3161_client_floor_excludes_cve_2026_33753(self) -> None:
        """Every declaration must exclude the TSA-impersonation bypass (<1.0.6).

        freeTSA is the default anchoring backend and the advisory's worked
        example, so a lower floor would undermine `verify`'s central guarantee.
        """
        declared = self._floors()["rfc3161-client"]
        assert declared, "rfc3161-client must declare a floor"
        for floor in declared:
            assert audit_mod._version_key(floor) >= audit_mod._version_key("1.0.6")

    def test_every_runtime_dependency_declares_a_floor(self) -> None:
        with open(REPO_ROOT / "pyproject.toml", "rb") as handle:
            pyproject = tomllib.load(handle)
        for req in audit_mod.collect_requirements(pyproject):
            if req.origin != "project.dependencies":
                continue
            assert req.floor is not None, f"{req.name} has no lower bound to audit"

    def test_floorless_requirements_are_all_allowlisted(self) -> None:
        """A new floorless requirement should fail here, not silently skip the audit."""
        with open(REPO_ROOT / "pyproject.toml", "rb") as handle:
            pyproject = tomllib.load(handle)
        floorless = {
            r.name for r in audit_mod.collect_requirements(pyproject) if not r.floor
        }
        assert floorless <= audit_mod.NO_FLOOR_EXPECTED
