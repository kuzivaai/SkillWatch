"""SkillWatch CLI — periodic URL content monitoring for AI skills."""

import argparse
import hashlib
import json as json_mod
import sys
import time

from pathlib import Path

from . import __version__, anchoring
from .cloak import PERSONAS, check_url
from .detector import detect_suspicious_changes, max_severity
from .differ import content_changed, generate_diff
from .fetcher import DEFAULT_USER_AGENT, fetch_url, strip_escape_sequences
from .formatter import (
    bold, dim, green, red, yellow,
    format_alert_detail, format_history, format_ledger, format_scan_result,
    format_scan_summary, format_url_table, severity_icon, severity_label,
)
from .parser import extract_urls_from_file
from .sarif import build_sarif
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


# Shown at the bottom of `skillwatch --help` and on the no-argument screen.
# Leads with concrete examples: users reach for examples before flag lists
# (clig.dev, lucasfcosta, ThoughtWorks all recommend "lead with examples").
_EXAMPLES = """\
Examples:
  skillwatch add SKILL.md              Watch every URL a skill file points to
  skillwatch add-url https://a.co/x    Watch a single page
  skillwatch scan                      Check all watched pages for changes now
  skillwatch alerts                    See what changed, in plain language
  skillwatch alert 1                   Full detail for one alert, with the diff
  skillwatch sources                   Re-check watched skill files for changes
  skillwatch verify                    Check the tamper-evident ledger is intact
  skillwatch anchor                    Externally timestamp the ledger head (RFC 3161)

First run:
  skillwatch add-url https://example.com && skillwatch scan

Run it regularly with cron or GitHub Actions - see the README.
Docs: https://github.com/kuzivaai/SkillWatch
"""


def _safe(url: str) -> str:
    """Strip escape sequences from a URL before printing to terminal."""
    return strip_escape_sequences(url)


def _content_fp(text: str) -> str:
    """Short fingerprint of an alert's diff, stored with feedback for audit."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16] if text else ""


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
        description="Periodic URL content monitoring for AI skills and MCP tools",
        epilog=_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
        "--output", choices=["text", "json", "sarif"], default="text",
        help="Output format: text (default), json (for jq/webhooks), or sarif (for GitHub Code Scanning)",
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

    # status
    status_p = sub.add_parser("status", help="Show monitoring summary")
    _add_db_arg(status_p)

    # list
    list_p = sub.add_parser("list", help="List all monitored URLs")
    _add_db_arg(list_p)

    # sources
    sources_p = sub.add_parser("sources", help="Re-check tracked skill/config files for changes (definition drift)")
    _add_db_arg(sources_p)

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
    _fb_group = alert_p.add_mutually_exclusive_group()
    _fb_group.add_argument(
        "--dismiss", action="store_true",
        help="Record this alert's flags as a false alarm (quietens them for this URL)",
    )
    _fb_group.add_argument(
        "--confirm", action="store_true",
        help="Record this alert's flags as real (cancels any quietening for this URL)",
    )
    _add_db_arg(alert_p)

    # feedback
    feedback_p = sub.add_parser(
        "feedback", help="Show or reset the false-alarm decisions you've recorded"
    )
    feedback_p.add_argument("--reset", action="store_true", help="Delete all recorded feedback")
    _add_db_arg(feedback_p)

    # verify
    verify_p = sub.add_parser(
        "verify", help="Check the tamper-evident content ledger is intact"
    )
    verify_p.add_argument(
        "--against", type=str, metavar="HEAD",
        help="A chain head you published earlier; confirms history up to it is unchanged",
    )
    _add_db_arg(verify_p)

    # ledger
    ledger_p = sub.add_parser(
        "ledger", help="Show or export the verifiable record of what URLs served"
    )
    ledger_p.add_argument("--limit", type=int, default=20, help="How many recent entries to show")
    ledger_p.add_argument(
        "--export", type=str, metavar="PATH",
        help="Write the full ledger to a portable JSON file anyone can re-verify",
    )
    _add_db_arg(ledger_p)

    # anchor
    anchor_p = sub.add_parser(
        "anchor",
        help="Externally timestamp the current ledger head (tamper-proof anchoring)",
    )
    anchor_p.add_argument(
        "--method", default=anchoring.DEFAULT_METHOD,
        help="Anchoring method (default: rfc3161)",
    )
    anchor_p.add_argument(
        "--tsa", default=anchoring.DEFAULT_TSA_URL,
        help="RFC 3161 Time-Stamp Authority URL",
    )
    anchor_p.add_argument(
        "--out", type=str, metavar="PATH",
        help="For --method rfc3161: also write the raw proof token here",
    )
    anchor_p.add_argument(
        "--repo", type=str, default=".", metavar="PATH",
        help="For --method git: the git repo to commit the anchor into (default: .)",
    )
    _add_db_arg(anchor_p)

    # cloak (stateless — no database needed)
    cloak_p = sub.add_parser(
        "cloak",
        help="Check if a URL serves different content to different clients (UA-based)",
    )
    cloak_p.add_argument("url", help="URL to check")

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        print(dim("\n  Get started: skillwatch add <SKILL.md>  then  skillwatch scan"))
        return 0

    if args.command == "cloak":
        return _cmd_cloak(args)

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
        elif args.command == "status":
            return _cmd_status(store)
        elif args.command == "list":
            return _cmd_list(store)
        elif args.command == "sources":
            return _cmd_sources(store, args)
        elif args.command == "history":
            return _cmd_history(store, args)
        elif args.command == "alerts":
            return _cmd_alerts(store, args)
        elif args.command == "alert":
            return _cmd_alert(store, args)
        elif args.command == "feedback":
            return _cmd_feedback(store, args)
        elif args.command == "verify":
            return _cmd_verify(store, args)
        elif args.command == "ledger":
            return _cmd_ledger(store, args)
        elif args.command == "anchor":
            return _cmd_anchor(store, args)
        else:
            parser.print_help()
            return 0
    finally:
        store.close()


def _cmd_cloak(args: argparse.Namespace) -> int:
    """Check whether a URL serves different content to different clients."""
    result = check_url(args.url)
    if not result.comparable:
        print(yellow(
            f"Could not compare {_safe(args.url)} "
            f"(only {len(result.ok_personas)} of {len(PERSONAS)} fetches succeeded)"
        ))
        return 2
    if result.varies:
        print(red(f"Content varies by client for {_safe(args.url)}"))
        for content_hash, personas in result.groups.items():
            print(f"  {content_hash[:12]}  {', '.join(personas)}")
        print(dim(f"  lowest pairwise similarity: {result.min_similarity}"))
        return 1
    print(green(
        f"Same content for all {len(result.ok_personas)} clients: {_safe(args.url)}"
    ))
    return 0


def _cmd_add(store: Store, args: argparse.Namespace) -> int:
    try:
        urls = extract_urls_from_file(args.file)
    except FileNotFoundError as exc:
        print(red(f"  Error: {exc}"), file=sys.stderr)
        print(dim("  Check the path, or pass a SKILL.md, .json, .yaml, or .txt file."), file=sys.stderr)
        return 1

    if not urls:
        print(yellow(f"  No URLs found in {args.file}"))
        return 0

    from .ssrf import SSRFError, validate_url

    added = 0
    skipped = 0
    blocked = 0
    for u in urls:
        try:
            validate_url(u["url"])
        except SSRFError:
            blocked += 1
            print(f"  {red('X')}  {_safe(u['url'])} (blocked: private/reserved)")
            continue
        _, is_new = store.add_url(u["url"], u["source_type"], u["source_path"])
        if is_new:
            added += 1
            print(f"  {green('+')}  {_safe(u['url'])}")
        else:
            skipped += 1

    # Record the source file's fingerprint so `skillwatch sources` can detect
    # if it is later edited or gains new references (a local rug-pull check).
    from .parser import source_fingerprint
    try:
        fp_hash, fp_urls = source_fingerprint(args.file)
        store.record_source(args.file, fp_hash, fp_urls)
    except OSError:
        pass

    parts = [f"Added {bold(str(added))} URL(s) from {args.file}"]
    if skipped:
        parts.append(f"{skipped} already monitored")
    print(f"\n  {', '.join(parts)}")
    if added == 0 and skipped == 0:
        print(
            red("  No monitorable URLs were added; correct or remove the blocked references and retry."),
            file=sys.stderr,
        )
        return 1
    print(dim("  Run 'skillwatch scan' to perform the initial check."))
    return 0


def _cmd_add_url(store: Store, args: argparse.Namespace) -> int:
    from .ssrf import SSRFError, validate_url

    try:
        validate_url(args.url)
    except SSRFError as exc:
        print(red(f"  Blocked: {exc}"), file=sys.stderr)
        print(dim("  SkillWatch only monitors public web pages, not private or local addresses."), file=sys.stderr)
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
    sarif_out = args.output == "sarif"
    machine_out = json_out or sarif_out

    if not urls:
        if sarif_out:
            print(json_mod.dumps(build_sarif([]), indent=2))
        elif json_out:
            print(json_mod.dumps({"status": "empty", "message": "No URLs to scan"}))
        else:
            print(dim("  No URLs to scan. Use 'skillwatch add <file>' to start."))
        return 0

    # Merge preset patterns with user-supplied patterns
    ignore_patterns = list(args.ignore_pattern)
    if args.preset != "none" and args.preset in _PRESETS:
        ignore_patterns = _PRESETS[args.preset] + ignore_patterns

    if not machine_out:
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
        prog = f"[{i + 1}/{total}]"

        result = fetch_url(
            url,
            timeout=args.timeout,
            user_agent=args.user_agent or DEFAULT_USER_AGENT,
            ignore_patterns=ignore_patterns or None,
        )

        if not result.ok:
            errors += 1
            store.add_snapshot(url_id, "", None, error=result.error, status_code=result.status_code)
            if machine_out:
                json_results.append({"url": url, "status": "error", "error": result.error})
            elif not args.quiet:
                print(format_scan_result(url, False, error=result.error, progress=prog))
            continue

        prev = store.get_latest_good_snapshot(url_id)

        new_snap_id = store.add_snapshot(
            url_id, result.content_hash, result.content_text,
            raw_html=result.raw_html,
            raw_html_hash=result.raw_html_hash, status_code=result.status_code,
        )

        if prev is None:
            unchanged += 1
            if machine_out:
                json_results.append({"url": url, "status": "baseline"})
            elif not args.quiet:
                print(format_scan_result(url, False, progress=prog))
            continue

        if not content_changed(prev["content_hash"], result.content_hash):
            unchanged += 1
            if machine_out:
                json_results.append({"url": url, "status": "unchanged"})
            elif not args.quiet:
                print(format_scan_result(url, False, progress=prog))
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
        demoted = store.demoted_flags(url_id)

        store.add_alert(
            url_id,
            prev_snapshot_id=prev["id"],
            new_snapshot_id=new_snap_id,
            diff_text=diff_text,
            flags=flag_codes,
            severity=severity,
        )
        alerts_created += 1

        if machine_out:
            json_results.append({
                "url": url, "status": "changed", "severity": severity,
                "flags": [{"code": f.code, "severity": f.severity,
                           "description": f.description, "evidence": f.evidence}
                          for f in flags],
            })
        else:
            print(format_scan_result(url, True, flags, progress=prog, demoted_flags=demoted))

    if sarif_out:
        changed_results = [r for r in json_results if r.get("status") == "changed"]
        print(json_mod.dumps(build_sarif(changed_results), indent=2))
    elif json_out:
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


def _cmd_status(store: Store) -> int:
    url_count = store.url_count()
    last_scan = store.last_scan_time()
    pending = store.pending_alert_count()

    print(f"\n{bold('  SkillWatch')} status\n")
    print(f"  URLs monitored:   {url_count}")
    print(f"  Last scan:        {last_scan or 'never'}")
    print(f"  Pending alerts:   {pending}")
    print(f"  Database:         {store.db_path}")

    if url_count == 0:
        print(dim("\n  Get started: skillwatch add <SKILL.md>  then  skillwatch scan"))
    elif pending > 0:
        print(f"\n  Run {bold('skillwatch alerts')} to view details.")
    print()
    return 0


def _cmd_list(store: Store) -> int:
    urls = store.get_urls()
    print(f"\n{bold('  SkillWatch')} — {len(urls)} URLs monitored\n")
    print(format_url_table(urls))
    print()
    return 0


def _cmd_sources(store: Store, args: argparse.Namespace) -> int:
    """Re-read tracked source files and report definition drift.

    Detects when a SKILL.md or MCP config that was added is later edited or
    gains new URL references (a local 'rug pull'). New references are added to
    monitoring. Exits 1 if any tracked file changed.
    """
    from .parser import source_fingerprint
    from .ssrf import SSRFError, validate_url

    sources = store.get_sources()
    if not sources:
        print(dim("\n  No source files tracked. 'skillwatch add <file>' records one.\n"))
        return 0

    print(bold(f"\n  {len(sources)} source file(s) tracked\n"))
    drift = 0
    for s in sources:
        path = s["path"]
        try:
            cur_hash, cur_urls = source_fingerprint(path)
        except OSError:
            print(f"  {yellow('?')}   {_safe(path)}  {dim('(missing, cannot re-read)')}")
            continue

        if cur_hash == s["content_hash"]:
            print(f"  {green('OK')}  {_safe(path)}  {dim('(unchanged)')}")
            continue

        drift += 1
        old_urls = set(s["urls"])
        new_urls = set(cur_urls)
        added = sorted(new_urls - old_urls)
        removed = sorted(old_urls - new_urls)
        print(f"  {red('!!')}  {_safe(path)}  {red('changed since it was added')}")
        for u in added:
            try:
                validate_url(u)
            except SSRFError:
                print(f"       {red('X')} new reference (blocked): {_safe(u)}")
                continue
            store.add_url(u, "skill_md", path)
            print(f"       {green('+')} new reference (now monitored): {_safe(u)}")
        for u in removed:
            print(f"       {red('-')} reference removed: {_safe(u)}")
        if not added and not removed:
            print(dim("       (file edited; referenced URLs unchanged)"))
        # Update the stored fingerprint so the next check compares to the latest.
        store.record_source(path, cur_hash, cur_urls)

    print()
    if drift:
        print(f"  {red(str(drift))} source file(s) changed. New references are now monitored. Run {bold('skillwatch scan')}.")
        print(dim("  If you did not change these files yourself, treat the skill as compromised."))
    return 1 if drift else 0


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
        flags = flags if isinstance(flags, list) else []
        demoted = store.demoted_flags(a["url_id"])
        flag_str = ", ".join(f"{c} (dismissed)" if c in demoted else str(c) for c in flags)
        reviewed = " (reviewed)" if a.get("reviewed") else ""
        print(f"  {icon} #{a['id']}  {_safe(a['url'])[:80]}  {severity_label(severity)}  {dim(flag_str)}{dim(reviewed)}")

    print(f"\n  Run {bold('skillwatch alert <id>')} for details.")
    return 0


def _cmd_alert(store: Store, args: argparse.Namespace) -> int:
    alert = store.get_alert(args.id)
    if not alert:
        print(yellow(f"  Alert #{args.id} not found."))
        return 1

    if args.dismiss or args.confirm:
        decision = "dismissed" if args.dismiss else "confirmed"
        flags = alert.get("flags", []) or []
        content_fp = _content_fp(alert.get("diff_text") or "")
        for code in flags:
            store.record_flag_feedback(alert["url_id"], str(code), decision, content_fp)
        if args.dismiss:
            store.mark_alert_reviewed(args.id)
            alert["reviewed"] = 1
        print(green(f"  Recorded {len(flags)} flag(s) as {decision} for {_safe(alert['url'])}."))

    if args.review:
        store.mark_alert_reviewed(args.id)
        alert["reviewed"] = 1
        print(green(f"  Alert #{args.id} marked as reviewed."))

    demoted = store.demoted_flags(alert["url_id"])
    print(format_alert_detail(alert, demoted_flags=demoted))
    return 0


def _cmd_feedback(store: Store, args: argparse.Namespace) -> int:
    if args.reset:
        removed = store.reset_flag_feedback()
        print(green(f"  Cleared {removed} feedback record(s)."))
        return 0
    rows = store.list_flag_feedback()
    if not rows:
        print(dim("  No feedback recorded yet. "
                  "Use 'skillwatch alert <id> --dismiss' to quieten a false alarm."))
        return 0
    print(bold(f"\n  {len(rows)} feedback record(s)\n"))
    for r in rows:
        print(f"  {str(r['decision']):<10} {str(r['flag_code']):<22} x{r['n']}  "
              f"{_safe(str(r['url']))[:60]}")
    print(dim("\n  A flag dismissed twice (and never confirmed) for a URL is shown as "
              "'previously dismissed' on future alerts."))
    return 0


def _cmd_verify(store: Store, args: argparse.Namespace) -> int:
    """Recompute the ledger hash chain and report whether it is intact.

    With --against <head>, also confirm a head you published earlier is still
    part of the verified chain — which detects a rewrite of history up to it.
    """
    result = store.verify_ledger()
    against = getattr(args, "against", None)

    if result.entries == 0:
        print(dim("\n  The ledger is empty — nothing to verify yet."))
        print(dim("  Run 'skillwatch scan' to start recording what your URLs serve.\n"))
        return 0

    if not result.ok:
        print(f"\n  {red('!!')}  Ledger integrity check {red('FAILED')} at entry {bold('#' + str(result.broken_seq))}.")
        if result.reason:
            print(f"       {result.reason}")
        print(dim("  A past record was altered or removed. If you did not edit the database"))
        print(dim("  yourself, treat this monitoring history as compromised.\n"))
        return 1

    print(f"\n  {green('OK')}  Ledger verified: {bold(str(result.entries))} entries, chain intact.")
    print(dim("  Every recorded observation is unaltered and in original order."))
    print(f"  Current head: {result.head}")

    failed = False

    # Auto-check every recorded external anchor: its head must still be in the
    # chain (catches a rewrite of anchored history), and a cryptographic proof
    # is verified when the anchoring extra is installed.
    anchors = store.get_anchors()
    if anchors:
        print()
        for a in anchors:
            label = f"{a['method']} @ {a['anchored_time'] or a['created_at']}"
            short = a["head"][:16] + "…"
            if not store.ledger_contains_hash(a["head"]):
                print(f"  {red('!!')}  Anchor {red('DIVERGED')} ({label}): head {short} is no longer in the chain.")
                failed = True
                continue
            if a["proof"] and a["method"] == "rfc3161":
                if anchoring.anchoring_available():
                    if anchoring.verify_anchor(a["head"], a["method"], a["proof"]):
                        print(f"  {green('OK')}  Anchor verified ({label}): external timestamp binds this history.")
                    else:
                        print(f"  {red('!!')}  Anchor proof {red('INVALID')} ({label}).")
                        failed = True
                else:
                    print(f"  {dim('·')}   Anchor recorded ({label}); proof not cryptographically checked "
                          f"(install skillwatch[anchor]).")
            else:
                print(f"  {green('OK')}  Anchor present ({label}): head {short} still in the chain.")

    # Manual anchor check against a head the user published elsewhere.
    if against:
        if store.ledger_contains_hash(against):
            print(f"\n  {green('OK')}  Anchor matched: history up to your published head is intact.")
        else:
            print(f"\n  {red('!!')}  Ledger has {red('DIVERGED')} from the published anchor:")
            print(dim(f"       {against}"))
            print(dim("  That head is not in the current chain, so history before it was rewritten."))
            failed = True

    if not anchors and not against:
        print(dim("  Anchor it so a rewrite is detectable: run 'skillwatch anchor', or publish this"))
        print(dim("  head somewhere you do not control and re-check with 'skillwatch verify --against <head>'."))
    print()
    return 1 if failed else 0


def _cmd_anchor(store: Store, args: argparse.Namespace) -> int:
    """Externally timestamp the current ledger head so that a later rewrite of
    history up to it is detectable, even against a full-chain recompute."""
    result = store.verify_ledger()

    if result.entries == 0:
        print(dim("\n  The ledger is empty — nothing to anchor yet. Run 'skillwatch scan' first.\n"))
        return 1
    if not result.ok:
        print(f"\n  {red('!!')}  The ledger is broken at entry {bold('#' + str(result.broken_seq))}; "
              "resolve that before anchoring.\n")
        return 1

    head = result.head or ""
    if args.method == "rfc3161" and not anchoring.anchoring_available():
        print(red("\n  RFC 3161 anchoring is not installed."), file=sys.stderr)
        print(dim("  " + anchoring.INSTALL_HINT.replace("\n", "\n  ")), file=sys.stderr)
        return 1

    try:
        anchor = anchoring.anchor_head(
            head, method=args.method, tsa_url=args.tsa, repo_path=args.repo
        )
    except anchoring.AnchorError as exc:
        print(red(f"\n  Anchoring failed: {exc}"), file=sys.stderr)
        return 1

    store.record_anchor(
        seq_covered=result.entries, head=head, method=anchor.method,
        external_ref=anchor.external_ref, proof=anchor.proof, anchored_time=anchor.timestamp,
    )
    print(f"\n  {green('OK')}  Anchored head {bold(head[:16] + '…')} via {anchor.method}.")
    if anchor.timestamp:
        print(dim(f"  Attested time: {anchor.timestamp}  (source: {anchor.external_ref})"))
    if args.out:
        try:
            Path(args.out).write_bytes(anchor.proof)
            print(dim(f"  Proof token written to {args.out} — preserve or publish it."))
        except OSError as exc:
            print(red(f"  (could not write {args.out}: {exc})"), file=sys.stderr)
    print(dim("  Re-check anytime with 'skillwatch verify'; a rewrite of anchored history will be caught.\n"))
    return 0


def _cmd_ledger(store: Store, args: argparse.Namespace) -> int:
    """Show recent ledger entries, or export the full ledger as portable JSON."""
    if args.export:
        try:
            n = store.export_ledger_to_file(args.export)
        except OSError as exc:
            print(red(f"  Error: could not write {args.export}: {exc}"), file=sys.stderr)
            print(dim("  Check the path is writable, then try again."), file=sys.stderr)
            return 1
        print(f"\n  {green('+')}  Exported {bold(str(n))} ledger entries to {args.export}")
        print(dim("  Anyone can re-verify it: skillwatch.ledger.verify_chain(payload['entries']).\n"))
        return 0

    entries = store.get_ledger(limit=args.limit)
    if not entries:
        print(dim("\n  The ledger is empty. Run 'skillwatch scan' to record observations.\n"))
        return 0

    print(format_ledger(entries, store.ledger_count()))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
