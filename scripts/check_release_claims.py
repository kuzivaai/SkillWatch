#!/usr/bin/env python3
"""Blocking pre-release gate: does the artefact we are about to publish carry a stale claim?

This is THE GATE. It runs offline, is deterministic, and can pass today.

It checks two things, because they can differ:

1. `README.md` on disk — what a reader of the repository sees.
2. The `Description` field of a freshly built sdist's `PKG-INFO` — what PyPI will
   actually render. This is the one that matters. The README is the *input* to
   the long description; a packaging change, a `dynamic` field, or a
   `readme = ...` edit could make them diverge, and the published page is what
   users read.

Why this is separate from `check_published_claims.py`: that script asks "is the
*live* page correct?", which cannot be true until after a release, so gating on
it would deadlock — the release is the only thing that makes the live page
correct. This script asks "is what we are about to publish correct?", which can
be true before a release, so it is safe to block on.

Usage:
    python3 scripts/check_release_claims.py [--skip-build]

Exit codes:
    0  no claim violations in README or the built sdist's PKG-INFO
    1  at least one violation — do not release
    2  the check could not be completed (build failed, PKG-INFO unreadable)
"""
from __future__ import annotations

import argparse
import email
import glob
import importlib.util
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Any


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


def build_sdist(into: str) -> str:
    """Build an sdist into `into` and return its path."""
    subprocess.run(
        [sys.executable, "-m", "build", "--sdist", "--outdir", into],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    made = glob.glob(os.path.join(into, "*.tar.gz"))
    if not made:
        raise RuntimeError(f"build produced no sdist in {into}")
    return made[0]


def description_from_sdist(sdist_path: str) -> str:
    """Extract the long description from an sdist's PKG-INFO."""
    with tarfile.open(sdist_path) as tar:
        members = [m for m in tar.getmembers() if m.name.endswith("PKG-INFO")]
        if not members:
            raise RuntimeError(f"no PKG-INFO in {sdist_path}")
        # Shallowest path is the top-level PKG-INFO.
        member = min(members, key=lambda m: m.name.count("/"))
        handle = tar.extractfile(member)
        if handle is None:
            raise RuntimeError(f"could not read {member.name}")
        raw = handle.read().decode("utf-8", errors="replace")
    message = email.message_from_string(raw)
    payload = message.get_payload()
    if isinstance(payload, str) and payload.strip():
        return payload
    # Older metadata versions put it in a header instead.
    return str(message.get("Description", ""))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="check README.md only. Reports the reduced coverage; does not hide it.",
    )
    args = parser.parse_args()

    # claim_rules is loaded dynamically, so its NamedTuple is not a static type here.
    violations: list[Any] = []

    readme = REPO_ROOT / "README.md"
    if not readme.exists():
        print("FAIL: README.md is missing.", file=sys.stderr)
        return 2
    violations += claim_rules.find_violations(
        readme.read_text(encoding="utf-8"), source="README.md"
    )
    print("Checked README.md")

    if args.skip_build:
        print(
            "WARNING: --skip-build was passed, so the sdist PKG-INFO was NOT checked.\n"
            "         README.md is the input to the long description, not the artefact.\n"
            "         Do not treat this run as a release gate."
        )
    else:
        with tempfile.TemporaryDirectory() as tmp:
            try:
                sdist = build_sdist(tmp)
                description = description_from_sdist(sdist)
            except (subprocess.CalledProcessError, RuntimeError, tarfile.TarError) as exc:
                print(f"FAIL: could not build or read the sdist: {exc}", file=sys.stderr)
                print("A gate that could not inspect its subject has not passed.", file=sys.stderr)
                return 2
            if not description.strip():
                print("FAIL: the sdist PKG-INFO carries an empty description.", file=sys.stderr)
                return 2
            violations += claim_rules.find_violations(description, source="sdist PKG-INFO")
            print(f"Checked sdist PKG-INFO ({len(description)} chars) from {os.path.basename(sdist)}")

    print()
    print(claim_rules.format_violations(violations))
    if violations:
        print("\nDo not release. Correct the claims first.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
