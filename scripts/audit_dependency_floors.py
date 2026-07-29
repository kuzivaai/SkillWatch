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
                },
                indent=2,
            )
        )
    else:
        audited = len([r for r in requirements if r.floor])
        print(f"Audited {audited} declared dependency floors.")
        for finding in findings:
            req = finding.requirement
            print(f"\n  {req.name}>={req.floor}  ({req.origin})")
            print(f"    permits versions with: {', '.join(finding.advisories)}")
            print(f"    minimum safe floor:    {finding.minimum_safe or 'none found'}")
        for req in without_floor:
            print(f"\n  {req.name}  ({req.origin}) declares NO lower bound")
            print("    every published release is permitted, including any older than")
            print("    the advisory database's coverage. Give it a floor.")
        if not findings and not without_floor:
            print("All declared floors are clear of known advisories.")
            print("Every declared requirement has a lower bound.")

    return 1 if (findings or without_floor) else 0


if __name__ == "__main__":
    sys.exit(main())
