"""Terminal output formatting."""

import sys


def _safe_url(url: str) -> str:
    """Strip escape sequences from URLs before terminal display."""
    from .fetcher import strip_escape_sequences
    return strip_escape_sequences(url)


# ANSI colour codes (disabled if not a TTY)
def _supports_colour() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


_COLOUR = _supports_colour()


def _c(code: str, text: str) -> str:
    if not _COLOUR:
        return text
    return f"\033[{code}m{text}\033[0m"


def red(text: str) -> str:
    return _c("31", text)


def yellow(text: str) -> str:
    return _c("33", text)


def green(text: str) -> str:
    return _c("32", text)


def bold(text: str) -> str:
    return _c("1", text)


def dim(text: str) -> str:
    return _c("2", text)


def severity_icon(severity: str) -> str:
    icons = {"critical": red("!!"), "warning": yellow("! "), "info": dim("i ")}
    return icons.get(severity, "  ")


def severity_label(severity: str) -> str:
    labels = {
        "critical": red("CRITICAL"),
        "warning": yellow("WARNING"),
        "info": dim("info"),
    }
    return labels.get(severity, severity)


def status_icon(open_alerts: int, last_checked: str | None) -> str:
    if not last_checked:
        return dim("--")
    if open_alerts > 0:
        return red("!!")
    return green("OK")


def format_url_table(urls: list[dict]) -> str:
    """Format a list of URLs as a terminal table."""
    if not urls:
        return dim("  No URLs being monitored. Use 'skillwatch add <file>' to start.")

    lines = [
        bold(f"  {'Status':<6}  {'URL':<60}  {'Last Checked':<20}  {'Alerts'}"),
        "  " + "-" * 100,
    ]

    for u in urls:
        status = status_icon(u.get("open_alerts", 0), u.get("last_checked"))
        raw_url = _safe_url(u["url"])
        url_display = raw_url[:58] + ".." if len(raw_url) > 60 else raw_url
        last = u.get("last_checked", "never") or "never"
        if last != "never":
            last = last[:19]  # trim microseconds
        alerts = u.get("open_alerts", 0)
        alert_str = red(str(alerts)) if alerts > 0 else dim("0")
        lines.append(f"  {status:<6}  {url_display:<60}  {last:<20}  {alert_str}")

    return "\n".join(lines)


def format_scan_result(url: str, changed: bool, flags: list | None = None, error: str | None = None) -> str:
    """Format a single scan result line."""
    url = _safe_url(url)
    if error:
        return f"  {red('ERR')}  {url}\n       {dim(_safe_url(error))}"

    if not changed:
        return f"  {green('OK ')}  {url}"

    if flags:
        max_sev = max((f.severity for f in flags), key=lambda s: {"info": 0, "warning": 1, "critical": 2}.get(s, 0))
        icon = severity_icon(max_sev)
        flag_codes = ", ".join(f.code for f in flags)
        return f"  {icon}  {url}\n       {severity_label(max_sev)}: {flag_codes}"

    return f"  {yellow('CHG')}  {url}  {dim('(content changed, no suspicious patterns)')}"


def format_scan_summary(total: int, unchanged: int, changed: int, alerts: int, errors: int) -> str:
    """Format scan summary."""
    parts = [
        f"\n  Scanned {bold(str(total))} URLs:",
        f"  {green(str(unchanged))} unchanged",
    ]
    if changed > 0:
        parts.append(f"  {yellow(str(changed))} changed")
    if alerts > 0:
        parts.append(f"  {red(str(alerts))} alerts created")
    if errors > 0:
        parts.append(f"  {red(str(errors))} errors")
    return " | ".join(parts)


def format_alert_detail(alert: dict) -> str:
    """Format a single alert with full details."""
    lines = [
        "",
        bold(f"  Alert #{alert['id']}"),
        f"  URL:      {_safe_url(alert['url'])}",
        f"  Detected: {alert['detected_at']}",
        f"  Severity: {severity_label(alert['severity'])}",
        f"  Reviewed: {'Yes' if alert['reviewed'] else 'No'}",
    ]

    flags = alert.get("flags", [])
    if flags:
        lines.append("  Flags:")
        for f in flags:
            lines.append(f"    - {f}")

    if alert.get("diff_text"):
        from .fetcher import strip_escape_sequences
        lines.append("")
        lines.append(bold("  Diff:"))
        for line in alert["diff_text"].splitlines()[:50]:
            line = strip_escape_sequences(line)  # defence in depth
            if line.startswith("+"):
                lines.append(f"  {green(line)}")
            elif line.startswith("-"):
                lines.append(f"  {red(line)}")
            else:
                lines.append(f"  {line}")
        diff_lines = alert["diff_text"].splitlines()
        if len(diff_lines) > 50:
            lines.append(dim(f"  ... ({len(diff_lines) - 50} more lines)"))

    return "\n".join(lines)


def format_history(url: str, snapshots: list[dict]) -> str:
    """Format snapshot history for a URL."""
    if not snapshots:
        return dim(f"  No history for {_safe_url(url)}")

    lines = [
        bold(f"  History for {_safe_url(url)}"),
        f"  {'Fetched At':<22}  {'Hash':<16}  {'Status'}",
        "  " + "-" * 60,
    ]

    prev_hash = None
    for s in reversed(snapshots):
        ts = s["fetched_at"][:19]
        h = s["content_hash"][:12] + ".."
        if s.get("error"):
            status = red(f"error: {_safe_url(s['error'])}")
        elif prev_hash and s["content_hash"] != prev_hash:
            status = yellow("CHANGED")
        elif prev_hash is None:
            status = dim("initial")
        else:
            status = green("unchanged")
        prev_hash = s["content_hash"]
        lines.append(f"  {ts:<22}  {h:<16}  {status}")

    return "\n".join(lines)
