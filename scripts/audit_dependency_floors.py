#!/usr/bin/env python3
"""Fail if any declared dependency floor permits a known-vulnerable version.

`pip-audit` audits the versions actually *installed*, which in CI are the newest
ones a resolver picks. That silently misses a whole class of defect: a floor such
as `rfc3161-client>=1.0` is satisfied by versions carrying published CVEs, so any
downstream user resolving against an older index, a lockfile, or a constrained
environment can legitimately install a vulnerable build while CI stays green.

SkillWatch is a security tool. It must not permit a resolution to a known-vulnerable
dependency, so the floors themselves are audited here, against the OSV database.

Usage:
    python3 scripts/audit_dependency_floors.py [--pyproject PATH] [--json]

Exit codes:
    0  every declared floor is free of known advisories
    1  at least one floor permits a known-vulnerable version
    2  the audit could not be completed (network, parse error)
"""
from __future__ import annotations

import argparse
import enum
import json
import sys
import urllib.error
import urllib.request
from typing import Any, NamedTuple

try:  # tomllib is stdlib from 3.11; tomli is the dev-extra backport for 3.10.
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - only taken on Python 3.10
    import tomli as tomllib

OSV_BATCH_URL = "https://api.osv.dev/v1/querybatch"
PYPI_JSON_URL = "https://pypi.org/pypi/{name}/json"
TIMEOUT = 30
RETRIES = 3

# There is no allowlist. A requirement with no lower bound is the maximum-exposure
# case, not an exempt one: it permits every release ever published, including any
# that predate the advisory database's coverage. Auditing only declared floors
# would be blind to exactly the dependencies at greatest risk.
#
# This is not hypothetical. `pytest-cov` had no floor, and the lowest-direct CI leg
# duly resolved it to 0.6 — a release from 2010 — while the audit reported success.


class Requirement(NamedTuple):
    name: str
    floor: str | None
    origin: str  # which table of pyproject.toml it came from


class Finding(NamedTuple):
    requirement: Requirement
    advisories: list[str]
    minimum_safe: str | None


def _canonical(name: str) -> str:
    """PEP 503 normalisation, so `confusable_homoglyphs` and `pyyaml` match the index."""
    out = []
    for char in name.lower():
        out.append(char if char.isalnum() else "-")
    collapsed = "-".join(part for part in "".join(out).split("-") if part)
    return collapsed


def parse_requirement(spec: str, origin: str) -> Requirement | None:
    """Pull the package name and its `>=` floor out of a requirement string.

    Deliberately narrow: this audits floors, so a requirement with no `>=` has no
    floor to audit and is returned with `floor=None`.
    """
    text = spec.split(";", 1)[0].strip()  # drop any environment marker
    if not text:
        return None

    for index, char in enumerate(text):
        if char in "<>=!~ [(":
            name, rest = text[:index], text[index:]
            break
    else:
        return Requirement(_canonical(text), None, origin)

    if rest.lstrip().startswith("["):  # extras, e.g. requests[socks]>=2.0
        closing = rest.index("]")
        rest = rest[closing + 1 :]

    floor = None
    for clause in rest.split(","):
        clause = clause.strip()
        if clause.startswith(">="):
            floor = clause[2:].strip()
            break
        if clause.startswith("=="):
            floor = clause[2:].strip()
            break
    return Requirement(_canonical(name), floor, origin)


def collect_requirements(pyproject: dict[str, Any]) -> list[Requirement]:
    """Every requirement declared anywhere in pyproject.toml, with its origin."""
    found: list[Requirement] = []

    for spec in pyproject.get("build-system", {}).get("requires", []):
        if (req := parse_requirement(spec, "build-system.requires")) is not None:
            found.append(req)

    project = pyproject.get("project", {})
    for spec in project.get("dependencies", []):
        if (req := parse_requirement(spec, "project.dependencies")) is not None:
            found.append(req)

    for extra, specs in project.get("optional-dependencies", {}).items():
        for spec in specs:
            if (req := parse_requirement(spec, f"optional-dependencies.{extra}")) is not None:
                found.append(req)

    return found


def _http_json(request: urllib.request.Request) -> Any:
    last: Exception | None = None
    for _ in range(RETRIES):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = exc
    raise RuntimeError(f"request failed after {RETRIES} attempts: {last}")


def pypi_versions(name: str) -> list[str]:
    """Non-yanked release versions on PyPI, in index order.

    Yanked releases are excluded: a resolver will not select them for a range, so
    treating them as reachable would report exposure that cannot actually occur.
    """
    request = urllib.request.Request(PYPI_JSON_URL.format(name=name))
    data = _http_json(request)
    versions = []
    for version, files in data.get("releases", {}).items():
        if not files:
            continue
        if all(f.get("yanked") for f in files):
            continue
        versions.append(version)
    return versions


def python_support_targets(pyproject: dict[str, Any]) -> list[tuple[int, int]]:
    """Python versions the project claims to support, from its own classifiers.

    Read from `Programming Language :: Python :: X.Y` rather than hardcoded, so
    the check follows the project's declared support instead of drifting from it.
    """
    targets = []
    for classifier in pyproject.get("project", {}).get("classifiers", []):
        parts = [p.strip() for p in classifier.split("::")]
        # "Programming Language :: Python :: 3.10" -> three parts, version last.
        # The bare "Programming Language :: Python :: 3" entry has no minor and is
        # skipped by the two-component check below.
        if len(parts) == 3 and parts[0] == "Programming Language" and parts[1] == "Python":
            bits = parts[2].split(".")
            if len(bits) == 2 and all(b.isdigit() for b in bits):
                targets.append((int(bits[0]), int(bits[1])))
    return sorted(set(targets))


class SpecifierVerdict(enum.Enum):
    """Three-valued result of evaluating a requires_python specifier.

    Deliberately not a bool. The previous boolean version returned True both for
    "this Python is permitted" and for "I could not parse this clause", which
    meant a typo like `=>3.10` sailed through the audit as a pass. Those are
    different answers and callers must be forced to distinguish them.

    ALLOWED is truthy; EXCLUDED and UNEVALUABLE are both falsey, so a caller who
    writes `if verdict:` fails closed rather than open.
    """

    ALLOWED = "allowed"
    EXCLUDED = "excluded"
    UNEVALUABLE = "unevaluable"

    def __bool__(self) -> bool:
        return self is SpecifierVerdict.ALLOWED


_OPERATORS = (">=", "<=", "==", "!=", "~=", ">", "<")


def evaluate_specifier(specifier: str | None, version: tuple[int, ...]) -> SpecifierVerdict:
    """Evaluate a PEP 440 requires_python specifier against a version tuple.

    Deliberately hand-rolled rather than importing `packaging`: this project
    forbids relying on an undeclared dependency, and `packaging` is not one of
    ours. Handles the operators that actually appear in requires_python metadata.

    Anything this parser does not understand — an unrecognised operator, a bound
    that is not a dotted numeric version — returns UNEVALUABLE. The caller must
    treat that as an audit problem. An auditor that silently passes input it
    could not read is worse than no auditor, because it reports confidence it
    has not earned.
    """
    if not specifier:
        return SpecifierVerdict.ALLOWED
    for clause in specifier.split(","):
        clause = clause.strip()
        if not clause:
            continue
        op = next((candidate for candidate in _OPERATORS if clause.startswith(candidate)), None)
        if op is None:
            return SpecifierVerdict.UNEVALUABLE
        bound = _parse_version_strict(clause[len(op) :].strip())
        if bound is None:
            return SpecifierVerdict.UNEVALUABLE
        trimmed = version[: len(bound)] if len(bound) < len(version) else version
        excluded = (
            (op == ">=" and not version >= bound)
            or (op == ">" and not version > bound)
            or (op == "<=" and not version <= bound)
            or (op == "<" and not version < bound)
            or (op == "==" and trimmed != bound)
            or (op == "!=" and trimmed == bound)
            or (op == "~=" and not version >= bound)
        )
        if excluded:
            return SpecifierVerdict.EXCLUDED
    return SpecifierVerdict.ALLOWED


def check_floor_python_compatibility(
    requirement: Requirement, targets: list[tuple[int, int]]
) -> str | None:
    """Return a problem description if the floor version is missing or unusable.

    Catches a floor that names a version which does not exist, or one whose
    `requires_python` excludes a Python the project claims to support.

    This does NOT prove installability. A release can satisfy requires_python and
    still have no wheel for a given interpreter, and then either build from sdist
    or fail outright. Only the lowest-direct CI matrix proves the floor actually
    resolves and runs. See docs/DEPENDENCY-FLOORS.md.
    """
    assert requirement.floor is not None
    url = f"https://pypi.org/pypi/{requirement.name}/{requirement.floor}/json"
    try:
        data = _http_json(urllib.request.Request(url))
    except RuntimeError:
        return f"floor {requirement.floor} could not be retrieved from PyPI (does it exist?)"

    requires_python = data.get("info", {}).get("requires_python")
    verdicts = {t: evaluate_specifier(requires_python, t) for t in targets}

    # Report "cannot read this" separately from "this excludes a Python we
    # support". Collapsing them would let unparseable metadata leave the audit
    # looking clean.
    unevaluable = [t for t, v in verdicts.items() if v is SpecifierVerdict.UNEVALUABLE]
    if unevaluable:
        return (
            f"floor {requirement.floor} declares requires_python={requires_python!r}, "
            f"which could not be evaluated against supported Python "
            f"{', '.join(f'{t[0]}.{t[1]}' for t in unevaluable)} — "
            f"the audit cannot confirm this floor is usable"
        )

    excluded = [f"{t[0]}.{t[1]}" for t, v in verdicts.items() if v is SpecifierVerdict.EXCLUDED]
    if excluded:
        return (
            f"floor {requirement.floor} declares requires_python={requires_python!r}, "
            f"which excludes supported Python {', '.join(excluded)}"
        )
    return None


def _parse_version_strict(version: str) -> tuple[int, ...] | None:
    """Parse a dotted numeric version, or return None if it is not one.

    The strict counterpart to `_version_key`. That function is a total ordering
    key for sorting real release versions off PyPI, where coercing an odd chunk
    to 0 is harmless. This one backs a correctness decision, so anything it
    cannot read must surface as "unknown" rather than as a number it invented.
    """
    if not version:
        return None
    parts: list[int] = []
    for chunk in version.split("."):
        if not chunk.isdigit():
            return None
        parts.append(int(chunk))
    return tuple(parts)


def _version_key(version: str) -> tuple[int, ...]:
    """Crude numeric ordering, adequate for picking a floor among release versions."""
    parts: list[int] = []
    for chunk in version.replace("-", ".").split("."):
        digits = "".join(c for c in chunk if c.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def osv_batch(queries: list[dict[str, Any]]) -> list[list[str]]:
    """Return the advisory IDs affecting each (package, version) query, in order."""
    if not queries:
        return []
    request = urllib.request.Request(
        OSV_BATCH_URL,
        data=json.dumps({"queries": queries}).encode(),
        headers={"Content-Type": "application/json"},
    )
    data = _http_json(request)
    results = []
    for entry in data.get("results", []):
        results.append([v["id"] for v in entry.get("vulns", [])])
    return results


def audit(requirements: list[Requirement]) -> tuple[list[Finding], list[Requirement]]:
    """Return (findings, requirements skipped for having no floor)."""
    with_floor = [r for r in requirements if r.floor]
    without_floor = [r for r in requirements if not r.floor]

    # One batch call for every declared floor.
    floor_queries = [
        {"package": {"name": r.name, "ecosystem": "PyPI"}, "version": r.floor} for r in with_floor
    ]
    floor_results = osv_batch(floor_queries)

    findings: list[Finding] = []
    for requirement, advisories in zip(with_floor, floor_results, strict=True):
        if not advisories:
            continue
        findings.append(Finding(requirement, sorted(advisories), _minimum_safe(requirement)))
    return findings, without_floor


def _minimum_safe(requirement: Requirement) -> str | None:
    """Lowest published version at or above the floor with no known advisories."""
    assert requirement.floor is not None
    try:
        candidates = pypi_versions(requirement.name)
    except RuntimeError:
        return None

    floor_key = _version_key(requirement.floor)
    higher = sorted(
        (v for v in candidates if _version_key(v) >= floor_key), key=_version_key
    )
    if not higher:
        return None

    queries = [
        {"package": {"name": requirement.name, "ecosystem": "PyPI"}, "version": v} for v in higher
    ]
    for version, advisories in zip(higher, osv_batch(queries), strict=True):
        if not advisories:
            return version
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pyproject", default="pyproject.toml")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    try:
        with open(args.pyproject, "rb") as handle:
            pyproject = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        print(f"error: could not read {args.pyproject}: {exc}", file=sys.stderr)
        return 2

    requirements = collect_requirements(pyproject)
    try:
        findings, without_floor = audit(requirements)
    except RuntimeError as exc:
        print(f"error: advisory lookup failed: {exc}", file=sys.stderr)
        return 2

    targets = python_support_targets(pyproject)
    compat: list[tuple[Requirement, str]] = []
    for requirement in requirements:
        if not requirement.floor:
            continue
        problem = check_floor_python_compatibility(requirement, targets)
        if problem:
            compat.append((requirement, problem))

    if args.json:
        print(
            json.dumps(
                {
                    "findings": [
                        {
                            "package": f.requirement.name,
                            "declared_floor": f.requirement.floor,
                            "origin": f.requirement.origin,
                            "advisories": f.advisories,
                            "minimum_safe": f.minimum_safe,
                        }
                        for f in findings
                    ],
                    "floorless": [
                        {"package": r.name, "origin": r.origin} for r in without_floor
                    ],
                    "python_incompatible": [
                        {"package": r.name, "origin": r.origin, "problem": p} for r, p in compat
                    ],
                },
                indent=2,
            )
        )
    else:
        audited = len([r for r in requirements if r.floor])
        supported = ", ".join(f"{t[0]}.{t[1]}" for t in targets)
        print(f"Audited {audited} declared dependency floors.")
        print(f"Declared Python support: {supported or '(none found in classifiers)'}")
        for finding in findings:
            req = finding.requirement
            print(f"\n  {req.name}>={req.floor}  ({req.origin})")
            print(f"    permits versions with: {', '.join(finding.advisories)}")
            print(f"    minimum safe floor:    {finding.minimum_safe or 'none found'}")
        for req in without_floor:
            print(f"\n  {req.name}  ({req.origin}) declares NO lower bound")
            print("    every published release is permitted, including any older than")
            print("    the advisory database's coverage. Give it a floor.")
        for req, problem in compat:
            print(f"\n  {req.name}>={req.floor}  ({req.origin})")
            print(f"    {problem}")
        if not findings and not without_floor and not compat:
            print("All declared floors are clear of known advisories.")
            print("Every declared requirement has a lower bound.")
            print("Every floor version exists and permits every supported Python.")
            print("(Installability is proven by the lowest-direct CI matrix, not here.)")

    return 1 if (findings or without_floor or compat) else 0


if __name__ == "__main__":
    sys.exit(main())
