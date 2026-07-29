# Hiding techniques: what `hidden_content` should and should not flag

Written 2026-07-29 before the detector was changed, so the corpus was built from
the taxonomy rather than from what the fix happened to catch. **Re-derived later
the same day against measured base rates** — see "The criterion that was missing".

## The question the check must answer

Not *"does this element's inline `style` attribute contain one of two lower-case
substrings"*. That was the old implementation and it is the wrong question — it
made the answer depend on capitalisation and on where the CSS happened to live.

The question is: **is this content concealed from a human reader while remaining
in the text an agent ingests?**

Both halves matter. Content removed from the DOM entirely is not a threat here —
the agent does not see it either. Content visible to a human is not concealed. The
threat is the gap between the two.

## The criterion that was missing

That question is necessary and **not sufficient**, and the first version of this
document treated it as both. Classifying on concealment alone cannot distinguish a
detection from a false-positive generator: a technique that conceals content **and
appears on most ordinary pages** is the latter. The document had no way to say so,
because it never asked how often each technique occurs legitimately.

Worse, a second criterion was in fact being applied — "is this a canonical
accessibility idiom?" — but only informally, to two techniques, and never written
down as a criterion. Two of the three assignments it produced were wrong (below).
An unwritten criterion cannot be checked, so it was applied inconsistently.

**Both criteria are now explicit, and the second is measured rather than assumed:**

> A technique belongs in the flagged bucket only if
> **(1)** it conceals content from a human while leaving it in the ingested text,
> **and (2)** it is rare enough on ordinary pages that flagging it is a signal
> rather than noise.

Criterion (2) needs a number, and until 2026-07-29 this project had none. It has
one now: `analysis/corpus/realpage/` — 201 pages, each referenced by a real
`SKILL.md` drawn from 157 distinct public repositories, none written by this
project. **No page in it carries a payload, so every occurrence counted is a
legitimate use.** Reproduce with `python3 analysis/measure_base_rate.py`.

## Measured base rate

```
technique                pages carrying it                          occurrences
display:none             103/201 (51.2%, 95% CI [44.4%, 58.1%])            337
visibility:hidden         73/201 (36.3%, 95% CI [30.0%, 43.2%])            111
opacity:0                 11/201 ( 5.5%, 95% CI [ 3.1%,  9.5%])             87
font-size:0                3/201 ( 1.5%, 95% CI [ 0.5%,  4.3%])             13
zero-box-clipped           2/201 ( 1.0%, 95% CI [ 0.3%,  3.6%])              6
offscreen-position         1/201 ( 0.5%, 95% CI [ 0.1%,  2.8%])              1
html-hidden-attr         111/201 (55.2%, 95% CI [48.3%, 61.9%])           1534
clip-path-inset           10/201 ( 5.0%, 95% CI [ 2.7%,  8.9%])             80
text-indent-negative       0/201 ( 0.0%, 95% CI [ 0.0%,  1.9%])              0
aria-hidden              141/201 (70.1%, 95% CI [63.5%, 76.0%])          12446
```

**The headline result: the taxonomy was excluding the rarer idioms and flagging
the commoner ones.** `clip-path` was excluded at 5.0% while the HTML `hidden`
attribute was flagged at 55.2%, and `text-indent` was excluded at 0.0% while
off-screen positioning — which is the *recommended* form of the same idiom — was
flagged.

## What the base rate does and does not license

`hidden_content` is a **delta** check. It flags content that is *newly* hidden,
not content that *is* hidden. Two gates in `cli.py` stand in front of it:

- `cli.py:434` — `if prev is None: ... continue`. A first fetch is a **baseline**
  and runs no detection at all.
- `cli.py:443` — detection runs only when the **extracted text hash** changed.

So prevalence is **not** a false-positive rate, and this document does not use it
as one. A page that permanently contains a collapsed accordion never produces an
alert. Prevalence measures *exposure*: how much concealed content sits on an
ordinary page, and therefore how much surface exists for a legitimate edit to
disturb. It bounds the risk from above; it does not estimate it.

What would estimate it is the delta measurement, and **that measurement is not yet
informative.** Across 199 paired snapshots the raw HTML changed on 97 (48.7%) but
the extracted text on only 3 (1.5%), and none of those 3 flagged. `0/3` has a 95%
interval of [0.0%, 56.1%]. The snapshots are minutes apart; editorial drift needs
days.

**REASONED, not evidenced.** The assignments below use prevalence as a proxy for
false-positive cost. The assumption is that a technique's chance of being disturbed
by a legitimate edit scales with how much of it is on the page. What would overturn
it: a days-apart delta measurement showing a technique with high prevalence and
near-zero churn — `html-hidden-attr` is the obvious candidate, since UI state is
toggled by script at runtime rather than rewritten by an editor. That is the single
measurement most worth taking next, and it is ledger item 37's remaining half.

## Bucket table

**This table is the specification.** `TECHNIQUE_BUCKETS` in `skillwatch/detector.py`
must match it exactly, and `tests/test_hiding_taxonomy.py` fails if it does not.
Identifiers are shared between the two.

| Technique | Bucket | Base rate | Verdict |
|---|---|---|---|
| `display:none` | a | 51.2% | Flagged. Highest-prevalence flagged technique; retained — see below. |
| `visibility:hidden` | a | 36.3% | Flagged. Same reasoning as `display:none`. |
| `opacity:0` | a | 5.5% | Flagged. Rare; survives the new criterion unchanged. |
| `font-size:0` | a | 1.5% | Flagged. Rare; survives unchanged. |
| `zero-box-clipped` | a | 1.0% | Flagged. Rare, and it does not fire on the canonical idiom — see below. |
| `offscreen-position` | b | 0.5% | **Moved out of (a).** It is the *recommended* `.sr-only` implementation. |
| `html-hidden-attr` | b | 55.2% | **Moved out of (a).** Standard UI-state primitive on 1 page in 2. |
| `clip-path-inset` | b | 5.0% | Not flagged, unchanged — but the value named was wrong. |
| `text-indent-negative` | b | 0.0% | Not flagged, unchanged. Now consistent with `offscreen-position`. |
| `aria-hidden` | c | 70.1% | Not flagged, unchanged. Inverse of the threat. |

Bucket meanings: **a** flagged; **b** conceals, but excluded because flagging it
fires on correct behaviour; **c** the inverse of the threat.

`<style>` block rules are **not** a technique and no longer appear as one. They are
a *delivery location* that applies to every technique above, resolved through
`soup.select`. Listing a location beside techniques in the original table was a
category error that made the table read as if moving CSS into a `<style>` block
were itself a way of hiding something.

## The primary source, quoted verbatim

Every accessibility claim below comes from WebAIM, *CSS in Action: Invisible
Content Just for Screen Reader Users*
(<https://webaim.org/techniques/css/invisiblecontent/>), fetched 2026-07-29. It is
quoted rather than paraphrased because the first version of this document
paraphrased an accessibility claim it had not checked, and got it backwards.

On off-screen positioning — **the heading is "Absolutely positioning content
off-screen" and the sentence introducing the rule is**:

> The following are the recommended styles for visually hiding content that will
> be read by a screen reader.

```css
.sr-only {
	position:absolute;
	left:-10000px;
	top:auto;
	width:1px;
	height:1px;
	overflow:hidden;}
```

On `text-indent`:

> text-indent: -10000px;
> This approach moves the content to the left 10000 pixels - thus off the visible
> screen. Screen readers will still read text with this style.
> However, if a link, form control, or other focusable element is given this
> style, the element would be focusable, but not visible on the page—sighted
> keyboard users would likely be confused. This approach may be a viable option if
> the element does not contain navigable elements, though better techniques are
> available.

On the clip technique — **the canonical ruleset, verbatim**:

```css
{clip: rect(1px, 1px, 1px, 1px);
clip-path: inset(50%);
height: 1px;
width: 1px;
margin: -1px;
overflow: hidden;
padding: 0;
position: absolute;}
```

On the HTML `hidden` attribute:

> The HTML hidden attribute is relatively new and not supported on older browsers
> like IE11. When supported, it functions the same as CSS display:none—elements
> with this attribute will not be presented to any user.

On zero-pixel sizing:

> An element with no height or width, whether defined in HTML or CSS, is typically
> removed from the flow of the page, so most screen readers will not read it. Do
> not size content to 0 pixels if you want the content to be read by a screen
> reader. […] All these techniques may result in search engine penalties as they
> may be interpreted as malicious.

## Per-technique derivation

Every assignment is re-derived below against both criteria, **including the ones
that do not move** — an assignment that survives a new criterion has to say so, or
a reader cannot tell it was reconsidered.

### `offscreen-position` — MOVED from (a) to (b)

Conceals: yes. Base rate: 0.5%, the rarest technique measured.

**Base rate alone would keep this flagged.** It is moved anyway, and the reason is
the accessibility criterion, now that the criterion is written down: WebAIM calls
`position:absolute; left:-10000px` *"the recommended styles"* for screen-reader-only
content. Flagging it means firing on the correct implementation of a standard
practice.

The original taxonomy had this in bucket (a) and `text-indent` in bucket (b),
describing `text-indent` as one of "the two canonical implementations". The primary
source says the opposite on both counts: off-screen absolute positioning is the
recommended one, and `text-indent` is the one for which "better techniques are
available". **The taxonomy flagged the recommended idiom and excluded the
deprecated one.** That is now corrected, and both forms of the same legacy idiom
sit in the same bucket, which resolves the inconsistency rather than papering over
it.

**Cost, stated:** corpus item `E-24` used off-screen positioning as an attack and
was caught. It is now a miss. This is a real reduction in detection, accepted
because the alternative is flagging every site that implements `.sr-only` the way
the primary accessibility source recommends.

**REASONED, not evidenced:** that legitimate `.sr-only` usage outweighs adversarial
usage of the same markup. The base rate shows the idiom is rare in absolute terms
(1/201), so this is the weakest assignment in the table on evidence. What would
overturn it: any real skill page found using off-screen positioning to carry a
payload. Cheapest to reverse: one character in `TECHNIQUE_BUCKETS`.

### `html-hidden-attr` — MOVED from (a) to (b)

Conceals: yes — WebAIM: "it functions the same as CSS display:none".

Base rate: **55.2% of pages, 1,534 occurrences** — the highest of any technique
that was being flagged, and the highest occurrence count of anything except
`aria-hidden`. A mean of about 14 hidden-attribute elements per page carrying it.

This is not a concealment technique in the sense the taxonomy is about. It is the
platform's own UI-state primitive: collapsed tab panels, closed dialogs, inactive
dropdown menus, `hidden` inputs carrying form tokens. Its entire purpose is state
that toggles during normal use. Flagging it means flagging the ordinary
construction of ordinary pages.

**Cost, stated:** corpus item `E-31` used the `hidden` attribute as an attack and
was caught. It is now a miss. Benign item `B-35` was a false positive and no longer
is.

This assignment is the one the measured data supports most strongly, and it is the
one criterion (1) alone could never have produced.

### `display:none` and `visibility:hidden` — RETAINED in (a), least comfortably

Conceals: yes. Base rate: **51.2%** and **36.3%** — comparable to
`html-hidden-attr`, which was just moved out on exactly this ground.

**This is the sharpest tension in the table and it is not resolved by evidence.**
The consistency argument says that if 55.2% evicts `html-hidden-attr`, 51.2% should
evict `display:none`. They are retained anyway, for reasons that are stated here so
a reader can disagree with them:

1. They are the canonical concealment *attack*, and the technique the whole flag
   was built for. Removing both would leave `hidden_content` catching `opacity:0`,
   `font-size:0` and collapsed boxes — a combined base rate of 8% and, on the
   synthetic corpus, three items.
2. Their high prevalence is overwhelmingly *static* — a collapsed accordion that
   is present in both snapshots produces no delta and therefore no alert. The
   `hidden` attribute differs in kind, not just degree: it is the primitive that
   script toggles at runtime, so its hidden set is the one that actually churns.
3. The flag is `info` severity and says "content is hidden here", which is true.

**Point 2 is REASONED, not evidenced, and it is the load-bearing one.** The delta
measurement that would confirm or refute it returned `0/3` — no information. It is
also contradicted by the source this document cites: WebAIM says the `hidden`
attribute "functions the same as CSS display:none". See *The split between
`html-hidden-attr` and `display:none`* above, which states the argument in full,
records that base rate does not separate the two, and fixes in advance what the
scheduled delta pass would have to show to move `display:none` as well.

### The split between `html-hidden-attr` and `display:none` — the weakest link, named

`html-hidden-attr` was moved out of the flagged bucket and `display:none` was kept
in it. **That split rests on one argument, and the source this document cites
argues against it.**

The two base rates are not distinguishable:

| Technique | Base rate | 95% CI | Bucket |
|---|---|---|---|
| `html-hidden-attr` | 111/201 (55.2%) | [48.3%, 61.9%] | b — not flagged |
| `display:none` | 103/201 (51.2%) | [44.4%, 58.1%] | a — flagged |

The intervals overlap across almost their whole width. **Base rate does not
separate these two techniques and cannot be cited as the reason they are in
different buckets.**

WebAIM, quoted verbatim above and the source this taxonomy relies on elsewhere,
says of the `hidden` attribute:

> When supported, it functions the same as CSS display:none—elements with this
> attribute will not be presented to any user.

**The primary source says they are the same mechanism.** So the split does not rest
on concealment behaviour either.

What it rests on is a **churn argument**, stated here so it can be attacked: that
the `hidden` attribute's prevalence is *dynamic* — it is the primitive script
toggles at runtime for tab panels, dialogs and dropdowns, so its hidden set changes
during ordinary use — while `display:none` prevalence is largely *static*, present
in both snapshots and therefore producing no delta. `hidden_content` is a delta
check, so only churning concealment costs a false positive.

**REASONED, not evidenced. This is the least supported decision in this document.**

- **Assumption:** that hidden-set churn, not hidden-set size, drives the delta
  false-positive rate, and that the two techniques differ in churn as much as this
  argument needs.
- **Evidence for it:** none measured. The delta pass that would test it returned
  `0/3` — no information.
- **Evidence against it:** the cited primary source calls the two mechanisms the
  same, and the base rates are statistically indistinguishable.
- **Cheapest to reverse:** one character in `TECHNIQUE_BUCKETS`.

**The test, and what each outcome means.** `analysis/run_delta_pass.py`, scheduled
for 2026-08-05 or later (ledger items 37, 38, 43):

| Delta pass result | What it means |
|---|---|
| `display:none` contributes **≥10%** of the delta false-positive rate | The churn argument fails. `display:none` should move to bucket (b) on the same reasoning that moved `html-hidden-attr`, and this section is the record that the outcome was predicted and accepted in advance. |
| `display:none` contributes **<10%**, and the rate is low overall | The churn argument survives its first real test. Record it as evidenced rather than reasoned. |
| Too few pages produce a text diff to measure at all | Neither. Say so, and do not treat a second uninformative result as support for the status quo. |

**A second outcome would also move it:** if `visibility:hidden` and `display:none`
churn together at a rate comparable to what `html-hidden-attr` would have
contributed, the eviction of `html-hidden-attr` was the arbitrary half of the
split, not the principled one.

### `zero-box-clipped` — RETAINED in (a)

Conceals: yes. Base rate: 1.0%.

Survives both criteria, and there is a specific reason it does not collide with the
accessibility exclusion: the canonical ruleset uses `height: 1px; width: 1px`, not
zero. The detector's rule requires a **zero** dimension with clipped overflow, so it
does not fire on `.sr-only`. WebAIM separately advises against zero-pixel sizing
and notes it "may result in search engine penalties as they may be interpreted as
malicious" — which is the same inference this tool draws.

### `opacity:0` and `font-size:0` — RETAINED in (a)

Conceals: yes. Base rates 5.5% and 1.5%. Neither is a documented accessibility
idiom; neither is common. Both survive unchanged. `opacity:0` is the higher of the
two and is worth watching: its 87 occurrences concentrate in a few pages using it
for animation and transitions, which is a legitimate pattern that a redesign could
make commoner.

### `clip-path-inset` — RETAINED in (b), but the documented value was wrong

Conceals: yes. Base rate: 5.0%.

The exclusion stands. **The value this document named did not.** It said
`clip-path: inset(100%)`. The canonical ruleset uses **`clip-path: inset(50%)`**,
alongside the older `clip: rect(1px, 1px, 1px, 1px)`. A reader implementing an
exclusion against `inset(100%)` would have been addressing a form the canonical
ruleset does not use.

The implementation was not affected, because `clip-path` is excluded by being
absent from the active declaration set rather than by matching a specific value —
so the error was confined to this document. That is luck, not design: had the
exclusion been written as a value match, it would have been inert in exactly the
way ledger item 36 records for the vacuous claim rule. The base-rate script matches
`inset(<any>%)` and `rect(...)`, so both canonical forms are counted.

### `text-indent-negative` — RETAINED in (b)

Conceals: yes. Base rate: 0.0% — not observed on any of the 201 pages.

Retained in (b), now for a stated reason rather than an assumed one. It is a
documented screen-reader technique that WebAIM still describes as "a viable
option", and it is the same legacy idiom as `offscreen-position`, which now shares
its bucket. Its measured base rate of zero means the assignment costs nothing
either way; it is kept excluded for consistency with the idiom it belongs to.

### `aria-hidden` — RETAINED in (c)

Base rate 70.1%, the commonest thing measured — and irrelevant to the decision,
because this is a category difference rather than a frequency one. `aria-hidden`
hides content from assistive technology **while leaving it visually present**. The
human sees it and the machine does not, which is the inverse of the threat.
Flagging it would be a category error at any base rate.

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

| Item | Technique | Legitimate use | After the re-derivation |
|---|---|---|---|
| B-33 | `display:none` | Collapsed accordion panel | still flagged — bucket (a) |
| B-34 | `clip-path` sr-only | Screen-reader-only link annotation | not flagged |
| B-35 | HTML `hidden` | Hidden form field and version marker | **no longer flagged** |
| B-36 | `text-indent` sr-only | Skip-to-content link | not flagged |
| B-37 | `<style>` block `display:none` | Changelog collapsed by default | still flagged — bucket (a) |

## Measurement history

### Before the concealment rewrite (2026-07-29)

```
Corpus: 37 benign / 10 adversarial A / 32 adversarial B
False-positive rate (overall):  5/37 (13.5%, 95% CI [5.9%, 28.0%])
Precision:      21/26 (80.8%, 95% CI [62.1%, 91.5%])
Overall recall: 21/42 (50.0%, 95% CI [35.5%, 64.5%])
Evasive recall: 11/32 (34.4%, 95% CI [20.4%, 51.7%])
  structural   0/10
```

### After the rewrite, before this re-derivation

```
False-positive rate (overall):  7/37 (18.9%, 95% CI [9.5%, 34.2%])
Precision:      29/36 (80.6%, 95% CI [65.0%, 90.2%])
Overall recall: 29/42 (69.0%, 95% CI [54.0%, 80.9%])
Evasive recall: 19/32 (59.4%, 95% CI [42.3%, 74.5%])
  structural   8/10
```

The two structural misses at that point were **E-07 and E-23** — both comment
injection, a technique outside this taxonomy. An earlier version of this document
named "E-23 and E-25"; `E-25` is recorded in the corpus as family `language` (a
Vietnamese instruction outside the 7-language pattern set), not `structural`. The
per-item family listing in `analysis/measure_efficacy.py` reconciles exactly with
the family totals; that sentence did not.

### After this re-derivation

See `SHIP-READINESS.md` and the README. Moving `offscreen-position` and
`html-hidden-attr` out of the flagged bucket costs corpus items `E-24` and `E-31`
and removes the `B-35` false positive.

## External validity

The synthetic figures are measured against a corpus this project wrote, including
the items each change was built to catch. They demonstrate that the implementation
does what this taxonomy says, and nothing about pages this project did not write.

The base rate above is the first figure here that is not self-authored. It closes
half of ledger item 37. **The other half — the delta false-positive rate at a
realistic interval — remains open, and no figure in this repository estimates it.**
