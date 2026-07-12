# Spec — Plane 1: on-device learning (no telemetry, no ML)

Implements the Plane-1 half of [ADR-0001](../adr/0001-two-plane-architecture.md).
Everything here runs on the user's machine and sends nothing. No ML.

> Invariant: nothing in this spec may open a user → server channel. The only
> outbound request permitted beyond the URLs the user watches is an **update
> check** to a public feed (§A), which is opt-out and reveals nothing about what
> the user watches.

## A. Signed pattern updates — "improve all the time"

The detector's rules become data, versioned and signed, distributed like
gitleaks/YARA/AV signatures. The detector code stays in `detector.py`; only the
rule *content* is updated.

### Feed format

A single published file (public GitHub raw / Pages), plus a detached signature:

```
patterns-<version>.json      # the ruleset
patterns-<version>.json.sig   # ed25519 signature over the file
```

`patterns.json`:

```json
{
  "feed_version": "2026.07.1",
  "min_tool_version": "0.3.0",
  "patterns": [
    {
      "id": "exec-curl-pipe-sh",
      "severity": "critical",
      "kind": "regex",
      "pattern": "curl\\s+[^|]+\\|\\s*(ba)?sh",
      "canonicalise": ["html_comment", "rot13", "reverse"],
      "provenance": "observatory:2026-07-02:skill/foo",  // real corpus event or "builtin"
      "added_feed_version": "2026.07.1"
    }
  ]
}
```

- `provenance` links each rule to the real Observatory event (Plane 2) that
  justified it, or `"builtin"`. This makes the feed auditable — a reviewer can
  trace every pattern to evidence. It also discharges the "named maintenance
  owner + cadence" readiness gate: the feed is the cadence.

### Mechanism (`skillwatch update`)

1. GET the feed index (a small `latest.json` naming the current version + hash).
2. If `feed_version` > local and `min_tool_version` ≤ installed version, download
   `patterns-<v>.json` + `.sig`.
3. **Verify** the ed25519 signature against a public key **shipped in the package**
   (`skillwatch/data/pattern-feed.pub`). Reject on mismatch — never apply an
   unsigned or badly-signed feed.
4. Atomically replace the local rules cache (`~/.skillwatch/patterns.json`);
   `detector.py` loads builtin rules ∪ cached feed rules at startup.
5. `--no-update` / `SKILLWATCH_OFFLINE=1` disables the check entirely. Document the
   residual clearly: an update check reveals only *"a SkillWatch instance polled the
   public feed"* — the same footprint as any `apt update`. It never transmits the
   user's URLs, configs, or results.

### Trust properties

- Signing key is offline/maintainer-held; only the public key ships.
- The feed is public and lives in git → fully auditable history of every rule change.
- Reuses the `cryptography` dependency already pulled by the `[anchor]` extra
  (ed25519 is in `cryptography`); no new hard dependency for the core install
  (feed verification can live behind the same optional extra, with a clear message
  if a user runs `update` without it).

## B. Local false-positive adaptation

The tool learns which flags **this user** repeatedly dismisses and quietens them —
100% on-device, counts only, no ML.

### Storage (`store.py`)

New table:

```sql
CREATE TABLE flag_feedback (
  flag_code   TEXT NOT NULL,
  url_id      INTEGER NOT NULL,
  content_fp  TEXT NOT NULL,   -- fingerprint of the flagged content span
  decision    TEXT NOT NULL,   -- 'dismissed' | 'confirmed'
  ts          TEXT NOT NULL,
  PRIMARY KEY (flag_code, url_id, content_fp, ts)
);
```

### Behaviour

- `skillwatch alert <id> --dismiss` / `--confirm` records a decision.
- On future scans, `formatter.py` demotes a flag to a "previously dismissed"
  low-priority line when the same `(flag_code, url_id, content_fp)` has been
  dismissed ≥ N times (default 2) and never confirmed. It is **shown, not hidden**
  — suppression is reversible and auditable (`skillwatch feedback --list/--reset`).
- Severity ordering still flows through `severity_rank()` (single source of truth);
  adaptation only adjusts *display priority*, never deletes a finding.

### Non-goals

No cross-user learning, no model, no network. Adaptation is per-machine and resets
with the local DB.

## C. Local multi-persona fetch (cloaking-lite) — optional

`fetcher.py` gains an optional mode: fetch each URL under a few local personas
(User-Agent + Accept-Language + headers), extract text, and compare hashes. If they
differ, emit a `content-varies-by-requester` signal (possible cloaking).

- Uses the existing SSRF/DNS-pinning path; **no proxies** → no geo variety, no new
  trust cost (still only contacts the watched URLs).
- Full geo/residential cloaking detection is Plane 2 (Apify) — see
  [spec Plane 2](plane-2-observatory.md). The comparison logic is shared
  (prototype: `prototypes/cloaking_prototype.py`).
- Off by default; `--personas` opt-in; respects "periodic, not continuous".

## Testing

- Feed: signature accept/reject, version gating, offline mode, atomic replace,
  builtin ∪ feed rule loading. A tampered feed must be rejected.
- FP adaptation: dismiss→demote after threshold; confirm cancels demotion; reset works.
- Cloaking-lite: shares `prototypes/cloaking_prototype.py` tests (clean vs varying).
- Per repo convention, every change ships with a test; ruff + mypy strict stay clean.

## Out of scope (restated)

Telemetry of any kind; ML; a user→server channel; continuous/daemon monitoring.
