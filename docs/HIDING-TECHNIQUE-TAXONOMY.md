# Hiding techniques: what `hidden_content` should and should not flag

Written 2026-07-29, before the detector was changed, so the corpus was built from
the taxonomy rather than from what the fix happened to catch.

## The question the check must answer

Not *"does this element's inline `style` attribute contain one of two lower-case
substrings"*. That was the old implementation and it is the wrong question — it
made the answer depend on capitalisation and on where the CSS happened to live.

The question is: **is this content concealed from a human reader while remaining
in the text an agent ingests?**

Both halves matter. Content removed from the DOM entirely is not a threat here —
the agent does not see it either. Content visible to a human is not concealed. The
threat is the gap between the two.

## Bucket (a) — in scope

Conceals from a human, stays in the text an agent ingests.

| Technique | Corpus item | Reasoning |
|---|---|---|
| `display:none` (any case) | E-26, E-27 | Removes the box entirely; text stays in the DOM |
| `visibility:hidden` (any case) | existing | Box reserved, contents unpainted |
| `position:absolute;left:-9999px` | E-24 | Painted outside the viewport |
| `opacity:0` | E-28 | Painted fully transparent |
| `font-size:0` | E-29 | Glyphs painted at zero size |
| `height:0;overflow:hidden` | E-30 | Box collapsed, overflow clipped |
| HTML `hidden` attribute | E-31 | The platform's own "not relevant" primitive |
| Same-document `<style>` block rule | E-32 | Identical effect; the old check only looked at inline styles, so moving one character of CSS into a `<style>` block defeated it |

Case-insensitivity is not a separate technique. It is the same technique, and
treating `DISPLAY:NONE` as different from `display:none` was a bug, not a scope
decision. CSS property names and keyword values are case-insensitive.

## Bucket (b) — accessibility idioms, deliberately NOT flagged

`clip-path: inset(100%)` and `text-indent: -9999px` are the two canonical
implementations of the `.sr-only` / visually-hidden pattern. They hide content
visually **while deliberately keeping it available to screen readers**.

**Decision: do not flag. REASONED, not evidenced.**

The reasoning, and its assumptions:

- These are the recommended implementations in every accessibility guide this
  project's author is aware of. A detector that fires on them fires on
  well-built sites, not on attacks.
- The cost lands on a gate that currently passes with little headroom. The benign
  false-positive rate is **4/32 (12.5%, 95% CI [5.0%, 28.1%])** against a ≤30%
  gate evaluated on the interval. The upper bound is already 28.1%. A rule that
  fires on a common idiom could push it over, and the gate would then be failing
  because of correct behaviour on benign pages.
- The technique is not thereby safe. An attacker can use `.sr-only` markup to
  conceal a payload, and this project will not catch it. That is a stated gap,
  not an oversight.

**Assumption:** that legitimate `.sr-only` usage is much more common on real pages
than adversarial usage of the same markup. Untested — this project has no
real-page corpus (ledger item 37).

**What would overturn it:** evidence that `.sr-only` markup is being used to carry
payloads in practice, or a real-page corpus showing the idiom is rarer than
assumed. Either would justify flagging it at a lower severity.

**Cheapest to reverse:** the visibility rules are a table in
`skillwatch/detector.py`. Moving a technique between buckets is a one-line change
plus a corpus item and a re-measure.

Benign corpus items **B-34** (clip-path sr-only label) and **B-36** (text-indent
skip link) exist specifically so a future change that starts flagging these shows
up immediately as a false positive rather than passing unnoticed.

## Bucket (c) — the inverse of the threat, excluded

`aria-hidden="true"` hides content from assistive technology **while leaving it
visually present to a sighted reader**. That is the opposite of the threat: the
human sees it and the machine does not.

Flagging it would be a category error. Excluded with no corpus item on the
adversarial side.

## Out of scope by hard boundary, not by effort

**External stylesheets** (`<link rel="stylesheet" href="...">`).

Resolving them requires fetching a URL the user never specified. This tool's
outbound traffic is limited to URLs the user explicitly asked it to watch; that is
a stated hard boundary, and following a stylesheet reference would breach it —
including the SSRF surface it would open.

Consequence, which must be stated wherever the flag's coverage is described:
**stylesheet-based hiding is handled for same-document `<style>` blocks and is
structurally out of reach for external stylesheets.** An attacker who moves the
rule into a linked stylesheet defeats this check, and no amount of implementation
effort changes that without breaching the boundary.

## Benign counterparts

A corpus containing only malicious uses of a technique makes any detector for it
look perfect. Each in-scope technique therefore has a legitimate counterpart:

| Item | Technique | Legitimate use |
|---|---|---|
| B-33 | `display:none` | Collapsed accordion panel |
| B-34 | `clip-path` sr-only | Screen-reader-only link annotation |
| B-35 | HTML `hidden` | Hidden form field and version marker |
| B-36 | `text-indent` sr-only | Skip-to-content link |
| B-37 | `<style>` block `display:none` | Changelog section collapsed by default |

B-33, B-35 and B-37 use bucket-(a) techniques legitimately. **They are expected to
be flagged** — the flag is `info` severity and means "content is hidden here",
which is true of a collapsed accordion. They are in the corpus so that the cost of
the rule is visible in the false-positive rate rather than hidden.
