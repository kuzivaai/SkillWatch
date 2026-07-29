# Pattern Provenance

Provenance table for every detection pattern in `skillwatch/detector.py`.
All patterns are regex-based heuristics. None provide guaranteed detection.

## Flag codes (13 total)

| # | Flag code | Severity | Source | Date added | Rationale |
|---|-----------|----------|--------|------------|-----------|
| 1 | `new_exec_command` | critical | Original (v0.1.0) | 2026-06-26 | Detects shell commands (curl, wget, pip install, eval, exec, subprocess, powershell) in added content. Core indicator of malicious payload delivery. |
| 2 | `new_base64` | warning | Original (v0.1.0) | 2026-06-26 | Flags base64-encoded strings (40+ chars) as potential obfuscated payloads. Excludes SRI hashes, hex-only digests, and URL-path-like strings. |
| 3 | `credential_reference` | warning | Original (v0.1.0) | 2026-06-26 | Flags references to api_key, secret, token, password, .env, private_key, access_key. Indicates potential data exfiltration instructions. |
| 4 | `new_domains` | warning | Original (v0.1.0) | 2026-06-26 | Flags URLs pointing to domains not present in the original content. Indicates potential redirect to attacker infrastructure. |
| 5 | `major_deletion` | warning | Original (v0.1.0) | 2026-06-26 | Flags >50% content removal. Could indicate content replacement attack. |
| 6 | `suspicious_script` | critical | v0.2.0 | 2026-06-26 | New `<script>` tags containing eval, document.cookie, fetch, XMLHttpRequest, WebSocket, atob, btoa. Diff-based (only new scripts flagged). |
| 7 | `prompt_injection` | critical | ATR-2026-00001 (MIT) | 2026-06-26 | 32 regex patterns derived from Agent Threat Rules. Covers 7 languages + obfuscation. See injection pattern table below. |
| 8 | `unicode_homoglyph` | warning | Unicode Consortium | 2026-06-26 | Characters from non-Latin scripts (Cyrillic, Greek, Cherokee, Armenian, Coptic, Myanmar, Georgian, Ethiopic, Osage, Lisu) that visually imitate Latin letters. Uses confusable_homoglyphs library. |
| 9 | `data_uri_payload` | warning | v0.2.0 | 2026-06-26 | data: URIs with text/html or application/javascript content type in added text. |
| 10 | `iframe_detected` | warning | v0.2.0 | 2026-06-26 | New `<iframe>` elements in HTML. Diff-based. |
| 11 | `hidden_content` | info | v0.2.0 | 2026-06-26 | New elements with display:none or visibility:hidden containing text. Diff-based. |
| 12 | `meta_refresh_redirect` | warning | v0.2.0 | 2026-06-26 | New `<meta http-equiv="refresh">` redirect. Diff-based. |
| 13 | `data_uri_embed` | critical | v0.2.0 | 2026-06-26 | New iframe/embed/object with data: URI source. Diff-based. |

## Prompt injection patterns (32 total)

Derived from ATR-2026-00001 (Agent Threat Rules, MIT licensed). Only the
subset applicable to static web page text is included; patterns requiring
conversation context (praise-redirect, task switching) are excluded.

| # | Category | Language | Description |
|---|----------|----------|-------------|
| 1 | Instruction override | English | Broad "ignore/disregard/forget previous instructions" |
| 2 | Instruction override | English | Forget-everything shorthand |
| 3 | Instruction override | English | Broad forget-everything variants |
| 4 | Instruction override | English | Ignore-above with action verb |
| 5 | Extraction | English | System prompt extraction requests |
| 6 | Persona | English | Persona switching ("you are now...") |
| 7 | Persona | English | Pretend-to-be-evil |
| 8 | Persona | English | Role redefinition |
| 9 | Override | English | Temporal override ("from now on...") |
| 10 | Override | English | New instruction assignment |
| 11 | Override | English | Authoritative compliance demands |
| 12 | Restriction removal | English | Hypothetical restriction removal |
| 13 | Delimiter | Multi | Fake system-level delimiters ([SYSTEM], <<SYS>>) |
| 14 | Obfuscation | N/A | Base64-encoded injection keywords |
| 15 | Obfuscation | N/A | Cyrillic/Greek homoglyph substitution |
| 16 | Obfuscation | N/A | Zero-width character insertion |
| 17 | Obfuscation | N/A | URL-encoded / hex-escaped keywords |
| 18 | Obfuscation | N/A | Spaced-out injection keywords |
| 19 | Override | English | ALL-CAPS embedded commands |
| 20 | Obfuscation | N/A | Markdown-hidden injection |
| 21 | Persona | English | Bare imperative "act as" |
| 22 | Obfuscation | N/A | Decode-and-execute instructions |
| 23 | Instruction override | German | ignoriere/vergiss/missachte + Anweisungen |
| 24 | Instruction override | German | vergiss/ignoriere alles |
| 25 | Override | German | neue Aufgabe/Anweisung |
| 26 | Instruction override | German | Formal (Sie) instruction override |
| 27 | Override | German | ACHTUNG STOPP |
| 28 | Instruction override | Spanish | ignora/olvida/descarta instrucciones |
| 29 | Instruction override | French | oubliez/ignorez instructions |
| 30 | Instruction override | Arabic | Injection keywords (7 terms) |
| 31 | Instruction override | Russian | zabud/ignoriruy + instruktsii |
| 32 | Instruction override | Serbian/Croatian | zaboravi/ignoriraj instrukcije |

## Canonicalisation layer

Before pattern matching, added text is pre-processed to decode:

| Transform | Description | Added |
|-----------|-------------|-------|
| HTML comments | Extracts text from `<!-- ... -->` | 2026-07-03 |
| Reversed text | Reverses spans containing command words when reversed | 2026-07-03 |
| ROT13 | Decodes ROT13 spans containing command words | 2026-07-03 |

Safety bounds: per-span cap 1,000 characters, total decoded cap 10,000 characters.

## Quarterly review log

`MAINTENANCE.md` ratifies a quarterly review in January, April, July and October.

### July 2026 — conducted 2026-07-29 (overdue)

Four steps are prescribed. Two were completed, one was completed with a caveat,
and one was **not** done; each is marked so that a reader can tell what this
review actually establishes.

**1. Check ATR upstream for new patterns — DONE, and it has moved.**

Upstream is `Agent-Threat-Rule/agent-threat-rules`, at tag **v3.5.11** with more
than 100 commits since 2026-06-26, the date these 32 patterns were derived. Two
are directly relevant:

- `fix(rules): cut benign false positives on 7 rules with no recall loss (#342)`
- `docs(rules): record why 00003 and 00502 were tightened (#344)`

SkillWatch's patterns have **not** been refreshed against these. A refresh is
warranted and is likely to improve precision, which is currently the weakest
demonstrated gate.

It is not done in this pass, deliberately: any change to `detector.py` triggers
the mandatory efficacy re-run, and folding a pattern refresh into the same change
that rebuilt the measurement would make the before/after comparison circular.
Refresh first, measure second, as separate changes.

**Provenance gap found:** this file records the source as "ATR-2026-00001" but
never records *which ATR version* the 32 patterns were taken from. Drift from
upstream therefore cannot be measured precisely — only observed to exist. Future
derivations should record the upstream tag.

**2. Check CSA, arXiv and advisory feeds for new attack techniques — NOT DONE.**

Not performed. This project's own standard forbids presenting unverified research
as verified, and a credible pass over these feeds means tracing claims to primary
sources, which was not done here. Recording it as complete would be worse than
recording it as outstanding. **This step remains outstanding for July 2026.**

One adjacent finding did come from advisory data this cycle, though it concerns a
dependency rather than a detection pattern: `rfc3161-client` floors permitted
CVE-2026-33753, fixed in 0.3.1. See `CHANGELOG.md`.

**3. Run the efficacy harness — DONE.**

```
Original corpus (67 items: 32 benign, 10 pattern-matching, 25 evasive)
  Precision      21/25 (84.0%, 95% CI [65.3%, 93.6%])
  Overall recall 21/35 (60.0%, 95% CI [43.6%, 74.4%])
  Evasive recall 11/25 (44.0%, 95% CI [26.7%, 62.9%])
  Benign FP       4/32 (12.5%, 95% CI [5.0%, 28.1%])

Holdout v2 (18 items; all 12 malicious items are evasive)
  Precision       9/10 (90.0%, 95% CI [59.6%, 98.2%])
  Overall recall  9/12 (75.0%, 95% CI [46.8%, 91.1%])

HTML corpus (12 items)  TP 6  FP 0  TN 6  FN 0
```

No detector change was made this cycle, so the `MAINTENANCE.md` regression gate
(precision ≥75%, recall ≥70% on any commit touching `detector.py`) was **not
triggered**. The measured figures fell because the evasive corpus was expanded
from 10 items to 25; behaviour on the original ten is unchanged. Reporting these
as a regression would be wrong.

**4. Record pattern changes — DONE.** No patterns were added, removed or
modified this cycle. Two items are carried forward:

| Carried forward | Detail |
|---|---|
| ATR refresh | Adopt upstream changes through v3.5.11, then re-measure. |
| `hidden_content` is narrower than documented | `_extract_hidden_texts()` (`detector.py:605`) matches only `display:none` and `visibility:hidden`. Corpus item `E-24` hides text with `position:absolute;left:-9999px` and is missed. Off-screen positioning, `clip-path`, `opacity:0`, `font-size:0` and `height:0` are all unhandled. This is a narrow implementation gap, not the semantic ceiling, and is fixable. |

## Changelog

| Date | Change | Impact |
|------|--------|--------|
| 2026-07-29 | Expanded the evasive corpus from 10 items to 25, preserving the original family proportions | Evasive recall re-measured at 11/25 (44.0%, CI [26.7%, 62.9%]); the n=10 figure of 50.0% had a CI of [23.7%, 76.3%] and demonstrated nothing. No detector change. |
| 2026-07-29 | Added Wilson score intervals to the efficacy harness; gates now evaluated on the CI lower bound | Three gates reclassified as not demonstrated. See `SHIP-READINESS.md`. |
| 2026-06-26 | Initial 13 flag codes, 32 injection patterns | v0.1.0 release |
| 2026-07-03 | Added canonicalisation layer (HTML comments, reversed text, ROT13) | Improved evasive recall from 30% to 50% on original corpus |
| 2026-07-03 | Added Osage, Lisu to homoglyph suspicious scripts | Extended Unicode coverage |
| 2026-07-03 | Added HTML sub-corpus (12 items) to efficacy harness | All 5 HTML flag codes now measured |
| 2026-07-03 | Fixed HTML checks running before early-return guard | Hidden content, meta refresh, data URI embed now detected when text diff is empty |
