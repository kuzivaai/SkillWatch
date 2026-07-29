#!/usr/bin/env python3
"""Non-gating report: does the LIVE PyPI page still carry a claim we have corrected?

This is THE REPORT, not a gate. Read the difference before wiring it anywhere.

`check_release_claims.py` asks: *is what we are about to publish correct?* That
can be true before a release, so it is safe to block on.

This script asks: *is what is currently published correct?* That cannot be made
true by anything except cutting a release. Gating a release on it would deadlock:
the live page stays stale until you release, and you cannot release until the
live page is not stale. Run it on a schedule or after a release. Never as a
precondition for one.

It answers two questions:

1. Do the shared claim rules fire against the live long description?
2. Does the live text diverge from `README.md` at HEAD in any claim-bearing
   region — i.e. has a correction been made in the repository that users cannot
   yet see?

A non-zero exit means "the published page does not match what this repository
says", which is the normal state between correcting a claim and releasing it. It
is a finding to act on, not a broken build.

**It also exits non-zero when it cannot reach PyPI.** A check that could not
inspect its subject has not passed, and must not be reported as green.

Usage:
    python3 scripts/check_published_claims.py [--package skillwatch] [--json]

Exit codes:
    0  the live page is clean and matches HEAD on every claim-bearing marker
    1  the live page carries a violation, or has drifted from HEAD
    2  PyPI could not be reached, or returned something unusable
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from types import ModuleType


def _load_claim_rules() -> ModuleType:
    """Load the shared rules by path.

    Deliberately importlib rather than `sys.path.insert` + a plain import: the
    latter is a module-level import after code, which needs a `# noqa: E402` to
    get past the linter, and this project does not suppress lint findings. The
    repository already uses this pattern in tests/test_dependency_floors.py.
    """
    spec = importlib.util.spec_from_file_location(
        "claim_rules", Path(__file__).resolve().parent / "claim_rules.py"
    )
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise RuntimeError("could not load scripts/claim_rules.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["claim_rules"] = module
    spec.loader.exec_module(module)
    return module


claim_rules = _load_claim_rules()

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPI_JSON = "https://pypi.org/pypi/{package}/json"
TIMEOUT_SECONDS = 30

# Short, distinctive strings that mark a claim-bearing region. Presence or
# absence of each is compared between HEAD's README and the live description.
# These are markers, not the rules: a rule says "this text is wrong", a marker
# says "this correction is or is not visible to users yet".
# Every marker here must be something README.md can plausibly contain, because
# the comparison is README-at-HEAD against the live description. A marker for a
# claim that lives only in another file (e.g. changedetection.io, which is in
# docs/COMPETITORS.md) is inert: absent from both sides, it can never differ, and
# it would sit in the list looking like coverage it does not provide.
CLAIM_MARKERS = (
    "three of the four",
    "six preventive mitigations",
    "Rescan continuously",
    "does not catch",
    "base-rate",
)


def fetch_live_description(package: str) -> tuple[str, str]:
    """Return (version, long_description) from PyPI, or raise."""
    request = urllib.request.Request(
        PYPI_JSON.format(package=package),
        headers={"Accept": "application/json", "User-Agent": "skillwatch-claims-check"},
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))
    info = payload.get("info", {})
    return info.get("version", "?"), info.get("description", "") or ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", default="skillwatch")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    try:
        version, live = fetch_live_description(args.package)
    except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError) as exc:
        message = (
            f"FAIL: could not reach PyPI for {args.package!r}: {exc}\n"
            "This check has NOT passed. A check that cannot inspect its subject "
            "has not verified anything."
        )
        print(message, file=sys.stderr)
        return 2

    if not live.strip():
        print(
            f"FAIL: PyPI returned an empty long description for {args.package} {version}.",
            file=sys.stderr,
        )
        return 2

    violations = claim_rules.find_violations(live, source=f"PyPI {args.package} {version}")

    readme_path = REPO_ROOT / "README.md"
    drift: list[str] = []
    if readme_path.exists():
        head = readme_path.read_text(encoding="utf-8")
        for marker in CLAIM_MARKERS:
            in_head = marker.lower() in head.lower()
            in_live = marker.lower() in live.lower()
            if in_head != in_live:
                where = "HEAD only" if in_head else "live only"
                drift.append(f"{marker!r}: {where}")
    else:
        drift.append("README.md missing from the repository — drift not computed")

    if args.json:
        print(
            json.dumps(
                {
                    "package": args.package,
                    "live_version": version,
                    "violations": [v._asdict() for v in violations],
                    "drift": drift,
                },
                indent=2,
            )
        )
    else:
        print(f"Live on PyPI: {args.package} {version} ({len(live)} chars)")
        print()
        print(claim_rules.format_violations(violations))
        print()
        if drift:
            print(f"{len(drift)} claim-bearing marker(s) differ between HEAD and the live page:")
            for entry in drift:
                print(f"  {entry}")
            print(
                "\n'HEAD only' means the correction exists in this repository but no user "
                "can see it yet. The only thing that fixes that is a release."
            )
        else:
            print("No claim-marker drift between HEAD and the live page.")

    return 1 if (violations or drift) else 0


if __name__ == "__main__":
    raise SystemExit(main())
