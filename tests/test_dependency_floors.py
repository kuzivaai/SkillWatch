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


class TestPythonSupportTargets:
    """Guards a bug that made the compatibility check silently vacuous.

    `"Programming Language :: Python :: 3.10"` splits into THREE parts, not four.
    An off-by-one in that check returned an empty target list, so every floor
    trivially "permitted every supported Python" and the audit still exited 0.
    """

    def test_reads_minor_versions_from_classifiers(self) -> None:
        pyproject = {
            "project": {
                "classifiers": [
                    "Development Status :: 3 - Alpha",
                    "Programming Language :: Python :: 3",
                    "Programming Language :: Python :: 3.10",
                    "Programming Language :: Python :: 3.13",
                ]
            }
        }
        assert audit_mod.python_support_targets(pyproject) == [(3, 10), (3, 13)]

    def test_real_pyproject_declares_the_full_matrix(self) -> None:
        assert audit_mod.python_support_targets(_pyproject()) == [
            (3, 10),
            (3, 11),
            (3, 12),
            (3, 13),
        ]

    def test_absent_classifiers_yield_no_targets(self) -> None:
        assert audit_mod.python_support_targets({}) == []


class TestSpecifierAllows:
    @pytest.mark.parametrize(
        ("specifier", "version", "expected"),
        [
            (">=3.9", (3, 10), True),
            (">=3.11", (3, 10), False),
            ("!=3.9.0,!=3.9.1,>=3.9", (3, 10), True),
            (">=3.9,<3.13", (3, 13), False),  # the case this check exists to catch
            (">=3.9,<3.13", (3, 12), True),
            (None, (3, 13), True),  # no declared bound permits everything
            ("", (3, 13), True),
        ],
    )
    def test_evaluates_requires_python(
        self, specifier: str | None, version: tuple[int, ...], expected: bool
    ) -> None:
        assert audit_mod.specifier_allows(specifier, version) is expected


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

    # Floors that are load-bearing for a specific, documented reason. Each entry
    # records why, so a later raise-or-lower decision is made on the reason and
    # not on taste. Network-free by construction: these are constants. Whether a
    # floor is *installable* is proven by the lowest-direct CI matrix, not here.
    KNOWN_GOOD_MINIMUMS = {
        "rfc3161-client": (
            "1.0.6",
            "CVE-2026-33753: TSA-impersonation bypass; freeTSA is our default backend",
        ),
        "wheel": (
            "0.46.2",
            "CVE-2026-24049: path traversal in `wheel unpack` (0.40.0-0.46.1)",
        ),
        "pyyaml": (
            "6.0.2",
            "first release publishing wheels across the whole 3.10-3.13 matrix; "
            "6.0 has no cp312/cp313 wheel and fails to build, 6.0.1 compiles from "
            "sdist on 3.13 and so needs a toolchain a user may not have",
        ),
        "cryptography": ("48.0.1", "lowest release free of published advisories"),
        "requests": ("2.33.0", "lowest release free of published advisories"),
        "setuptools": ("83.0.0", "lowest release free of published advisories"),
    }

    def test_load_bearing_floors_are_at_or_above_their_known_good_minimum(self) -> None:
        declared: dict[str, list[str]] = {}
        for req in audit_mod.collect_requirements(_pyproject()):
            if req.floor:
                declared.setdefault(req.name, []).append(req.floor)

        failures = []
        for name, (minimum, reason) in self.KNOWN_GOOD_MINIMUMS.items():
            floors = declared.get(name)
            if not floors:
                failures.append(f"{name}: no floor declared (expected >={minimum} — {reason})")
                continue
            for floor in floors:
                if audit_mod._version_key(floor) < audit_mod._version_key(minimum):
                    failures.append(f"{name}>={floor} is below >={minimum} — {reason}")
        assert not failures, "floors below their known-good minimum:\n  " + "\n  ".join(failures)

    def test_no_requirement_is_left_without_a_lower_bound(self) -> None:
        """A floorless requirement is the maximum-exposure case, not an exempt one.

        There is no allowlist. Without a bound, every release ever published is
        permitted — including releases older than the advisory database's
        coverage, which the floor audit then cannot reason about at all. This
        was not theoretical: `pytest-cov` had no floor and the lowest-direct CI
        leg resolved it to 0.6, a 2010 release, while the audit reported success.
        """
        floorless = {
            f"{r.name} ({r.origin})"
            for r in audit_mod.collect_requirements(_pyproject())
            if not r.floor
        }
        assert not floorless, f"requirements with no lower bound: {sorted(floorless)}"
