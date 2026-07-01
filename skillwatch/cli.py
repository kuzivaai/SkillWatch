"""SkillWatch CLI — continuous URL content monitoring for AI skills."""

import argparse
import json as json_mod
import sys
import time

from . import __version__
from .detector import detect_suspicious_changes, max_severity
from .differ import content_changed, generate_diff
from .fetcher import _DEFAULT_USER_AGENT, fetch_url, strip_escape_sequences
from .formatter import (
    bold, dim, green, red, yellow,
    format_alert_detail, format_history, format_scan_result,
    format_scan_summary, format_url_table, severity_icon, severity_label,
)
from .parser import extract_urls_from_file
from .store import Store

# Built-in ignore pattern presets. These cover the most common sources
# of false positives on documentation and setup pages.
_PRESETS: dict[str, list[str]] = {
    "docs": [
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",              # ISO 8601 timestamps
        r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",  # UUIDs
        r"\b[0-9]{10,13}\b",                                    # Unix timestamps (sec/ms)
        r"[?&](?:v|ver|version|_)=[\w.]+",                      # Query version params
        r"\b[a-f0-9]{20,40}\b",                                 # Build/commit hashes
        r"nonce=['\"][^'\"]+['\"]",                              # CSRF nonces
    ],
}


def _safe(url: str) -> str:
    """Strip escape sequences from a URL before printing to terminal."""
    return strip_escape_sequences(url)


def _add_db_arg(p: argparse.ArgumentParser) -> None:
    """Add --db to a subparser with SUPPRESS default.

    Using SUPPRESS means the attribute is only set if the user provides
    the flag, so it won't override the value from the parent parser.
    This lets --db work both before and after the subcommand:
      skillwatch --db /path scan
      skillwatch scan --db /path
    """
    p.add_argument("--db", type=str, default=argparse.SUPPRESS, help="Path to SQLite database")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skillwatch",
        description="Continuous URL content monitoring for AI skills and MCP tools",
    )
    parser.add_argument("--version", action="version", version=f"skillwatch {__version__}")
    parser.add_argument("--db", type=str, default=None, help="Path to SQLite database")

    sub = parser.add_subparsers(dest="command")

    # add
    add_p = sub.add_parser("add", help="Add URLs from a SKILL.md, MCP config, or URL list")
    add_p.add_argument("file", help="Path to SKILL.md, .json, .yaml, or .txt file")
    _add_db_arg(add_p)

    # add-url
    add_url_p = sub.add_parser("add-url", help="Add a single URL to monitor")
    add_url_p.add_argument("url", help="URL to monitor")
    _add_db_arg(add_url_p)

    # remove
    rm_p = sub.add_parser("remove", help="Stop monitoring a URL")
    rm_p.add_argument("url", help="URL to remove")
    _add_db_arg(rm_p)

    # scan
    scan_p = sub.add_parser("scan", help="Scan all monitored URLs for changes")
    scan_p.add_argument("--delay", type=float, default=1.0, help="Delay between requests (seconds)")
    scan_p.add_argument("--timeout", type=int, default=10, help="Request timeout (seconds)")
    scan_p.add_argument("--quiet", action="store_true", help="Only show changes and errors")
    scan_p.add_argument(
        "--output", choices=["text", "json"], default="text",
        help="Output format: text (default) or json (machine-readable, for piping to jq/webhooks)",
    )
    scan_p.add_argument(
        "--user-agent", type=str, default=None,
        help="Custom User-Agent string for HTTP requests",
    )
    scan_p.add_argument(
        "--preset", choices=["docs", "none"], default="none",
        help="Built-in ignore pattern preset: 'docs' strips timestamps, UUIDs, build hashes",
    )
    scan_p.add_argument(
        "--ignore-pattern", action="append", default=[],
        help="Regex pattern to strip from content before hashing (repeatable). "
             "Use to suppress timestamps, build hashes, etc.",
    )
    _add_db_arg(scan_p)

    # list
    list_p = sub.add_parser("list", help="List all monitored URLs")
    _add_db_arg(list_p)

    # history
    hist_p = sub.add_parser("history", help="Show change history for a URL")
    hist_p.add_argument("url", help="URL to show history for")
    _add_db_arg(hist_p)

    # alerts
    alerts_p = sub.add_parser("alerts", help="Show alerts")
    alerts_p.add_argument("--all", action="store_true", help="Include reviewed alerts")
    _add_db_arg(alerts_p)

    # alert
    alert_p = sub.add_parser("alert", help="Show alert details")
    alert_p.add_argument("id", type=int, help="Alert ID")
    alert_p.add_argument("--review", action="store_true", help="Mark as reviewed")
    _add_db_arg(alert_p)

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        print(dim("\n  Get started: skillwatch add <SKILL.md>  then  skillwatch scan"))
        return 0

    store = Store(db_path=args.db)

    try:
        if args.command == "add":
            return _cmd_add(store, args)
        elif args.command == "add-url":
            return _cmd_add_url(store, args)
        elif args.command == "remove":
            return _cmd_remove(store, args)
        elif args.command == "scan":
            return _cmd_scan(store, args)
        elif args.command == "list":
            return _cmd_list(store)
        elif args.command == "history":
            return _cmd_history(store, args)
        elif args.command == "alerts":
            return _cmd_alerts(store, args)
        elif args.command == "alert":
            return _cmd_alert(store, args)
        else:
            parser.print_help()
            return 0
    finally:
        store.close()


def _cmd_add(store: Store, args: argparse.Namespace) -> int:
    try:
        urls = extract_urls_from_file(args.file)
    except FileNotFoundError as exc:
        print(red(f"  Error: {exc}"), file=sys.stderr)
        return 1

    if not urls:
        print(yellow(f"  No URLs found in {args.file}"))
        return 0

    added = 0
    skipped = 0
    for u in urls:
        _, is_new = store.add_url(u["url"], u["source_type"], u["source_path"])
        if is_new:
            added += 1
            print(f"  {green('+')}  {_safe(u['url'])}")
        else:
            skipped += 1

    parts = [f"Added {bold(str(added))} URL(s) from {args.file}"]
    if skipped:
        parts.append(f"{skipped} already monitored")
    print(f"\n  {', '.join(parts)}")
    print(dim("  Run 'skillwatch scan' to perform the initial check."))
    return 0


def _cmd_add_url(store: Store, args: argparse.Namespace) -> int:
    from .ssrf import SSRFError, validate_url

    try:
        validate_url(args.url)
    except SSRFError as exc:
        print(red(f"  Blocked: {exc}"), file=sys.stderr)
        return 1

    _, is_new = store.add_url(args.url, "manual")
    if is_new:
        print(f"  {green('+')}  {_safe(args.url)}")
    else:
        print(f"  {dim('=')}  {_safe(args.url)} (already monitored)")
    print(dim("  Run 'skillwatch scan' to perform the initial check."))
    return 0


def _cmd_remove(store: Store, args: argparse.Namespace) -> int:
    if store.remove_url(args.url):
        print(f"  {red('-')}  Removed {_safe(args.url)}")
    else:
        print(yellow(f"  URL not found: {args.url}"))
    return 0


def _cmd_scan(store: Store, args: argparse.Namespace) -> int:
    urls = store.get_urls()
    json_out = args.output == "json"

    if not urls:
        if json_out:
            print(json_mod.dumps({"status": "empty", "message": "No URLs to scan"}))
        else:
            print(dim("  No URLs to scan. Use 'skillwatch add <file>' to start."))
        return 0

    # Merge preset patterns with user-supplied patterns
    ignore_patterns = list(args.ignore_pattern)
    if args.preset != "none" and args.preset in _PRESETS:
        ignore_patterns = _PRESETS[args.preset] + ignore_patterns

    if not json_out:
        print(bold(f"\n  Scanning {len(urls)} URLs...\n"))

    total = len(urls)
    unchanged = 0
    changed = 0
    alerts_created = 0
    errors = 0
    json_results: list[dict] = []

    for i, url_record in enumerate(urls):
        if i > 0 and args.delay > 0:
            time.sleep(args.delay)

        url = url_record["url"]
        url_id = url_record["id"]

        result = fetch_url(
            url,
            timeout=args.timeout,
            user_agent=args.user_agent or _DEFAULT_USER_AGENT,
            ignore_patterns=ignore_patterns or None,
        )

        if not result.ok:
            errors += 1
            store.add_snapshot(url_id, "", None, error=result.error, status_code=result.status_code)
            if json_out:
                json_results.append({"url": url, "status": "error", "error": result.error})
            elif not args.quiet:
                print(format_scan_result(url, False, error=result.error))
            continue

        prev = store.get_latest_good_snapshot(url_id)

        new_snap_id = store.add_snapshot(
            url_id, result.content_hash, result.content_text,
            raw_html=result.raw_html,
            raw_html_hash=result.raw_html_hash, status_code=result.status_code,
        )

        if prev is None:
            unchanged += 1
            if json_out:
                json_results.append({"url": url, "status": "baseline"})
            elif not args.quiet:
                print(format_scan_result(url, False))
            continue

        if not content_changed(prev["content_hash"], result.content_hash):
            unchanged += 1
            if json_out:
                json_results.append({"url": url, "status": "unchanged"})
            elif not args.quiet:
                print(format_scan_result(url, False))
            continue

        changed += 1
        diff_text = generate_diff(
            prev.get("content_text", "") or "",
            result.content_text or "",
            url=url,
        )

        flags = detect_suspicious_changes(
            old_text=prev.get("content_text"),
            new_text=result.content_text or "",
            diff_text=diff_text,
            old_html=prev.get("raw_html"),
            new_html=result.raw_html,
        )

        severity = max_severity(flags)
        flag_codes = [f.code for f in flags]

        store.add_alert(
            url_id,
            prev_snapshot_id=prev["id"],
            new_snapshot_id=new_snap_id,
            diff_text=diff_text,
            flags=flag_codes,
            severity=severity,
        )
        alerts_created += 1

        if json_out:
            json_results.append({
                "url": url, "status": "changed", "severity": severity,
                "flags": [{"code": f.code, "severity": f.severity,
                           "description": f.description, "evidence": f.evidence}
                          for f in flags],
            })
        else:
            print(format_scan_result(url, True, flags))

    if json_out:
        print(json_mod.dumps({
            "version": __version__,
            "total": total, "unchanged": unchanged, "changed": changed,
            "alerts": alerts_created, "errors": errors,
            "results": json_results,
        }, indent=2))
    else:
        print(format_scan_summary(total, unchanged, changed, alerts_created, errors))
        if alerts_created > 0:
            print(f"\n  Run {bold('skillwatch alerts')} to view details.")

    return 1 if alerts_created > 0 else 0


def _cmd_list(store: Store) -> int:
    urls = store.get_urls()
    print(f"\n{bold('  SkillWatch')} — {len(urls)} URLs monitored\n")
    print(format_url_table(urls))
    print()
    return 0


def _cmd_history(store: Store, args: argparse.Namespace) -> int:
    # Find URL ID
    urls = store.get_urls()
    url_record = next((u for u in urls if u["url"] == args.url), None)
    if not url_record:
        print(yellow(f"  URL not found: {args.url}"))
        return 1

    snapshots = store.get_snapshot_history(url_record["id"])
    print(format_history(args.url, snapshots))
    return 0


def _cmd_alerts(store: Store, args: argparse.Namespace) -> int:
    alerts = store.get_alerts(unreviewed_only=not args.all)
    if not alerts:
        print(green("  No open alerts."))
        return 0

    print(bold(f"\n  {len(alerts)} alert(s)\n"))
    for a in alerts:
        severity = a.get("severity", "info")
        icon = severity_icon(severity)
        flags = a.get("flags", [])
        flag_str = ", ".join(flags) if isinstance(flags, list) else str(flags)
        reviewed = " (reviewed)" if a.get("reviewed") else ""
        print(f"  {icon} #{a['id']}  {_safe(a['url'])[:60]}  {severity_label(severity)}  {dim(flag_str)}{dim(reviewed)}")

    print(f"\n  Run {bold('skillwatch alert <id>')} for details.")
    return 0


def _cmd_alert(store: Store, args: argparse.Namespace) -> int:
    alert = store.get_alert(args.id)
    if not alert:
        print(yellow(f"  Alert #{args.id} not found."))
        return 1

    if args.review:
        store.mark_alert_reviewed(args.id)
        alert["reviewed"] = 1
        print(green(f"  Alert #{args.id} marked as reviewed."))

    print(format_alert_detail(alert))
    return 0


if __name__ == "__main__":
    sys.exit(main())
