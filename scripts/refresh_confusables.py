#!/usr/bin/env python3
"""Refresh the Unicode confusables data used by confusable_homoglyphs.

The confusable_homoglyphs library (v3.3.1, last released January 2019)
ships with confusables data from approximately Unicode 11.0. The library's
own CLI has an `update` command that downloads fresh data from unicode.org.

This script wraps that process with error handling and provenance logging.
It updates the data IN-PLACE in the installed package directory (or the
CONFUSABLE_DATA environment variable if set).

Usage:
    python scripts/refresh_confusables.py

Requirements:
    - confusable_homoglyphs[cli] (needs click)
    - Network access to ftp://ftp.unicode.org

If the download fails (firewall, FTP blocked), the script reports the error
and exits non-zero. The existing frozen data remains intact.

Provenance:
    Source: https://www.unicode.org/Public/security/latest/confusables.txt
    Licence: Unicode Character Database Terms of Use
             https://www.unicode.org/copyright.html
    The confusables.txt file is part of the Unicode Security Mechanisms
    (UTS #39) and is freely redistributable.
"""

import json
import os
import sys
from datetime import datetime, timezone


def main() -> int:
    try:
        from confusable_homoglyphs import utils
    except ImportError:
        print("ERROR: confusable_homoglyphs is not installed.", file=sys.stderr)
        return 1

    data_dir = os.environ.get("CONFUSABLE_DATA", utils.PACKAGE_DIR)
    confusables_path = os.path.join(data_dir, "confusables.json")

    # Record pre-update state
    pre_count = 0
    if os.path.exists(confusables_path):
        with open(confusables_path) as f:
            pre_count = len(json.load(f))
    print(f"Pre-update: {pre_count} confusable entries in {confusables_path}")

    # Attempt update
    try:
        from confusable_homoglyphs.cli import generate_categories, generate_confusables
    except ImportError:
        print(
            "ERROR: confusable_homoglyphs CLI not available. "
            "Install with: pip install 'confusable_homoglyphs[cli]'",
            file=sys.stderr,
        )
        print(
            "\nManual alternative: download confusables.txt from "
            "https://www.unicode.org/Public/security/latest/confusables.txt "
            "and run the library's generate_confusables() function.",
            file=sys.stderr,
        )
        return 1

    print("Downloading categories from unicode.org...")
    try:
        generate_categories()
        print("  Categories updated.")
    except Exception as exc:
        print(f"ERROR downloading categories: {exc}", file=sys.stderr)
        print("Existing data is unchanged.", file=sys.stderr)
        return 1

    print("Downloading confusables from unicode.org...")
    try:
        generate_confusables()
        print("  Confusables updated.")
    except Exception as exc:
        print(f"ERROR downloading confusables: {exc}", file=sys.stderr)
        print("Existing data is unchanged (categories may have been updated).", file=sys.stderr)
        return 1

    # Record post-update state
    post_count = 0
    if os.path.exists(confusables_path):
        with open(confusables_path) as f:
            post_count = len(json.load(f))

    print(f"\nPost-update: {post_count} confusable entries")
    print(f"Delta: {post_count - pre_count:+d} entries")
    print(f"Updated at: {datetime.now(timezone.utc).isoformat()}")
    print(f"Data directory: {data_dir}")
    print(
        "\nSource: https://www.unicode.org/Public/security/latest/confusables.txt"
    )
    print("Licence: Unicode Character Database Terms of Use")

    return 0


if __name__ == "__main__":
    sys.exit(main())
