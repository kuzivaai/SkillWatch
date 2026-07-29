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
| 11 | `hidden_content` | info | v0.2.0 | 2026-06-26, rewritten 2026-07-29 | Content concealed from a human but left in the text an agent ingests. Covers, inline **or** same-document `<style>` block, case-insensitively: `display:none`, `visibility:hidden|collapse`, `opacity:0`, `font-size:0`, zero `height`/`width` with clipped overflow. **Not** covered: the HTML `hidden` attribute and off-screen absolute positioning (**both removed 2026-07-29** after their base rate was measured on 201 real pages — `hidden` appears on 55.2% of them, and off-screen positioning is the WebAIM-recommended `.sr-only` implementation), `clip-path`/`text-indent` `.sr-only` idioms, `aria-hidden` (inverse of the threat), and **external stylesheets, which are out of reach by hard boundary**: resolving one means fetching a URL the user never specified. Diff-based. Taxonomy: `docs/HIDING-TECHNIQUE-TAXONOMY.md`. |
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

**Provenance gap: CLOSED 2026-07-29.** See "Pattern provenance" below.

## Pattern provenance

Recorded 2026-07-29, closing ledger item 5. Until this section existed, drift from
upstream was observable but not measurable: this file named the source but never
the version.

| Pattern set | n | Upstream source | Version | Upstream commit | Derived |
|---|---|---|---|---|---|
| `prompt_injection` regexes | 32 | [Agent-Threat-Rule/agent-threat-rules](https://github.com/Agent-Threat-Rule/agent-threat-rules) (MIT), catalogued locally as ATR-2026-00001 | **v3.5.1 — inferred, see below** | `22463fc82033a427708e655f0549cf15aa8c75e6` | 2026-06-26 |
| All other flag codes (12) | — | Written for this project; no upstream | n/a | n/a | 2026-06-26 to 2026-07-03 |

### How the version was established, and what is inferred

**Evidenced.** The derivation date is `2026-06-26`, the date `skillwatch/detector.py`
first entered version control:

```
$ git log --date=short --reverse --pretty="%ad %h %s" -- skillwatch/detector.py | head -1
2026-06-26 45c2739 feat: SkillWatch v0.1.0 — continuous URL content monitoring for AI skills
```

**Evidenced.** On that date the newest upstream release was **v3.5.1**, published
2026-06-21. The next release, v3.5.3, did not appear until 2026-06-30 — four days
after derivation:

```
$ gh api repos/Agent-Threat-Rule/agent-threat-rules/releases --jq '.[] | "\(.tag_name)  \(.published_at)"'
v3.5.11  2026-07-14T13:31:13Z
...
v3.5.3   2026-06-30T05:33:59Z
v3.5.1   2026-06-21T10:25:38Z
v3.5.0   2026-06-15T18:19:29Z
```

**REASONED, not evidenced.** That v3.5.1 was the version *actually consulted* is an
inference from availability, not a record of the act. Nobody wrote it down at the
time, and no artefact in this repository names a version. The inference assumes the
derivation used a tagged release rather than an untagged `main`, and that it used
the newest available rather than an older one.

What would overturn it: any contemporaneous note, or a diff showing the 32 patterns
match an ATR revision other than v3.5.1. **A future session comparing against
upstream should treat v3.5.1 as a starting hypothesis to be checked, not a fact.**

Recording the honest alternative: "provenance unknown, established as of 2026-07-29"
would also have been usable. It is not used because the availability window is
narrow enough (one release, five days before derivation, next one four days after)
that naming it is more useful than declining to — provided the inference is labelled,
which it is.

### Rule going forward

Any future derivation records the upstream tag **and** commit SHA **in the same
commit that introduces the patterns**. This section exists because that was not done
once, and reconstructing it afterwards produced an inference where a fact was
available for free at the time.

Upstream is now at **v3.5.11** (`30b946b2218cce2e55445f5d6c841193192194d4`,
2026-07-14). The gap from v3.5.1 to v3.5.11 is what ledger item 4 proposes to adopt;
this section is what makes that diff computable, which is why item 5 blocked item 4.


**2. Check CSA, arXiv and advisory feeds for new attack techniques — NOT DONE.**

Not performed. This project's own standard forbids presenting unverified research
as verified, and a credible pass over these feeds means tracing claims to primary
sources, which was not done here. Recording it as complete would be worse than
recording it as outstanding. **This step remains outstanding for July 2026.**

One adjacent finding did come from advisory data this cycle, though it concerns a
dependency rather than a detection pattern: `rfc3161-client` floors permitted
CVE-2026-33753, fixed in 0.3.1. See `CHANGELOG.md`.

**3. Run the efficacy harness — DONE.**

**Figures as they stood at this review. Superseded twice on 2026-07-29 — by the
`hidden_content` rewrite and then by the base-rate reclassification. The current
figures are in `README.md` and `SHIP-READINESS.md`; reproduce with
`python3 analysis/measure_efficacy.py`. Kept here as the record of what this
review saw, not as a current claim.**

```
<!-- figures:exempt reason="dated quarterly-review record: what that review saw, explicitly superseded above" -->
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
<!-- figures:end -->

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
| `hidden_content` coverage (**code gap CLOSED 2026-07-29; residual gaps stated**) | The narrow implementation this row described — `soup.find_all(style=re.compile(r"display:\s*none|visibility:\s*hidden"))`, case-sensitive, inline-only — was replaced on 2026-07-29 by a parser that asks whether content is concealed from a human while remaining in the ingested text, resolving same-document `<style>` rules through `soup.select`. Residual gaps, each deliberate and each stated: **external stylesheets** (hard boundary — resolving one means fetching a URL the user never specified); **`.sr-only` idioms** `clip-path`, `text-indent`, and off-screen positioning (flagging them fires on the accessibility implementation WebAIM recommends); **the HTML `hidden` attribute** (on 55.2% of 201 real pages — a UI-state primitive, not a concealment technique); **`@media` and other nested at-rules** (the parser reports them unparsed rather than reading them, and nothing surfaces that to the flag). Taxonomy and measured base rates: `docs/HIDING-TECHNIQUE-TAXONOMY.md`. |

## Changelog

| Date | Change | Impact |
|------|--------|--------|
<!-- figures:exempt reason="changelog row: the figure measured at that change, superseded twice since" -->
| 2026-07-29 | Expanded the evasive corpus from 10 items to 25, preserving the original family proportions | Evasive recall re-measured at 11/25 (44.0%, CI [26.7%, 62.9%]); the n=10 figure of 50.0% had a CI of [23.7%, 76.3%] and demonstrated nothing. No detector change. |
<!-- figures:end -->
| 2026-07-29 | Added Wilson score intervals to the efficacy harness; gates now evaluated on the CI lower bound | Three gates reclassified as not demonstrated. See `SHIP-READINESS.md`. |
| 2026-06-26 | Initial 13 flag codes, 32 injection patterns | v0.1.0 release |
| 2026-07-03 | Added canonicalisation layer (HTML comments, reversed text, ROT13) | Improved evasive recall from 30% to 50% on original corpus |
| 2026-07-03 | Added Osage, Lisu to homoglyph suspicious scripts | Extended Unicode coverage |
| 2026-07-03 | Added HTML sub-corpus (12 items) to efficacy harness | All 5 HTML flag codes now measured |
| 2026-07-03 | Fixed HTML checks running before early-return guard | Hidden content, meta refresh, data URI embed now detected when text diff is empty |
