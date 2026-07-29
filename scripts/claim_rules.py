#!/usr/bin/env python3
"""Rules about claims this project makes concerning other people's work.

Why this is a module and not a pytest file
------------------------------------------
It used to be a pytest file. That file read four repository paths and nothing
else, and its own docstring said so: "these tests read the repository's own
published surfaces. They do not fetch anything."

The most public surface this project has is the PyPI long description, and it was
outside that set. So on 2026-07-29 the repository was corrected, the guard went
green, and the live page kept serving both distortions for the whole day. The
check passed because what it should have examined was out of scope — the same
fail-open shape as the dependency auditor treating an unparseable specifier as
satisfied, and as the `pytest.skip()` that once turned every guard green when a
surface was missing.

So the rules live here, take arbitrary text, and are run by three callers against
three different things:

- `tests/test_published_claims.py`  — repository files, in CI
- `scripts/check_release_claims.py` — README at HEAD and a built sdist's PKG-INFO
- `scripts/check_published_claims.py` — the live PyPI long description

What a rule can and cannot do
-----------------------------
A rule cannot tell whether a paraphrase is faithful; that needs a human with the
source open. What it can check is the mechanical precondition for anyone ever
noticing: that an attributed finding carries a link, and that the two specific
distortions this project actually shipped do not reappear as assertions.

Use versus mention
------------------
Correcting a bad claim requires naming it. These rules therefore run against
*assertive* text: markdown blockquotes (someone else's words) and sentences
carrying an explicit retraction marker (our words about a past error) are
stripped first. A future session that reintroduces a claim as a plain assertion
still trips the rule; a session that quotes it to retract it does not.
"""
from __future__ import annotations

import re
from typing import NamedTuple


class Violation(NamedTuple):
    """One rule breach in one piece of text."""

    rule: str
    message: str
    excerpt: str
    source: str


# Named third parties whose findings this project cites. Attributing work to a
# named outside party is exactly the case that needs a source link: the reader
# has no way to check it otherwise, and we have repeatedly got the details wrong
# when working from memory or from someone else's summary.
ATTRIBUTED_SOURCES: dict[str, str] = {
    "Trail of Bits": "blog.trailofbits.com",
    "OWASP": "owasp.org",
    "SIGIL": "arxiv.org",
    "Cloud Security Alliance": "cloudsecurityalliance.org",
}

URL_RE = re.compile(r"https?://[^\s)>\]\"']+")

RETRACTION_MARKERS: tuple[str, ...] = (
    "earlier version of this readme",
    "earlier version of this description",
    "an earlier version",
    "earlier draft",
    "corrected here",
    "corrected above",
    "is corrected",
    "gets garbled",
    "get garbled",
    "which we quote to correct",
)

# The hour belongs to building three of four attacks, not to bypassing scanners.
COMPRESSED_TOB_RE = re.compile(
    r"scanner[s]?[^.\n]{0,80}(?:is|was|were|are)\s+bypassed\s+in\s+under\s+an\s+hour",
    re.IGNORECASE,
)

# AST05 lists six preventive mitigations. This project covers one and part of two.
#
# The span is [^.]{0,160}, not [^.\n]{0,60}. The narrower original could never
# match: in the text it was written to catch, 94 characters and a newline sat
# between "mitigations" and "describe what this tool does". It was a vacuous
# rule — it passed against the pre-correction README, which is why it was not
# among the failures when that file was used as a fail-before fixture. Every
# negative rule here now has a positive fixture in tests/test_claim_rules.py
# proving it can fire; a rule that has never fired has not been tested.
MITIGATION_OVERCLAIM_RE = re.compile(
    r"mitigations[^.]{0,160}describe what this tool\s+does", re.IGNORECASE
)

# OWASP's sixth mitigation is "Rescan continuously". This project is periodic by
# design and must never restate that mitigation in its own vocabulary to make the
# fit look cleaner than it is.
REWORDED_CONTINUOUS_RE = re.compile(
    r"(?:mitigations?|lists?)[^.\n]{0,120}(?:repeated|periodic)\s+rescanning",
    re.IGNORECASE,
)


def assertive_text(text: str) -> str:
    """Return only the prose that speaks in the document's own voice."""
    kept = [ln for ln in text.splitlines() if not ln.lstrip().startswith(">")]
    flattened = " ".join(kept)
    sentences = re.split(r"(?<=[.!?])\s+", flattened)
    return " ".join(s for s in sentences if not any(m in s.lower() for m in RETRACTION_MARKERS))


def find_violations(text: str, *, source: str = "<text>") -> list[Violation]:
    """Return every claim-rule violation in `text`.

    The single entry point. `source` is a label used in messages only — a file
    path, "PyPI", "PKG-INFO", whatever identifies the text to a reader.
    """
    out: list[Violation] = []
    assertive = assertive_text(text)

    # Rule 1 — an attributed finding must link to the party it attributes to.
    urls = URL_RE.findall(text)
    for name, domain in sorted(ATTRIBUTED_SOURCES.items()):
        if name in text and not any(domain in u for u in urls):
            out.append(
                Violation(
                    rule="unsourced-attribution",
                    message=(
                        f"attributes a finding to {name!r} but links nowhere on "
                        f"{domain}. A reader cannot check it and neither can we."
                    ),
                    excerpt=name,
                    source=source,
                )
            )

    # Rule 2 — the compressed Trail of Bits claim must not be asserted.
    match = COMPRESSED_TOB_RE.search(assertive)
    if match:
        out.append(
            Violation(
                rule="tob-compressed-quantifier",
                message=(
                    "attaches 'under an hour' to bypassing scanners. The source "
                    "attaches it to conceiving and implementing three of the four "
                    "attacks; the fourth took a few hours."
                ),
                excerpt=match.group(0),
                source=source,
            )
        )

    # Rule 3 — citing Trail of Bits requires carrying their quantifier.
    if "Trail of Bits" in text and "three of the four" not in text:
        out.append(
            Violation(
                rule="tob-missing-quantifier",
                message=(
                    "cites Trail of Bits without the source's own quantifier "
                    "('three of the four malicious skills'). Scope and quantifier "
                    "travel with the finding."
                ),
                excerpt="Trail of Bits",
                source=source,
            )
        )

    # Rule 4 — the AST05 mitigations do not describe this tool.
    match = MITIGATION_OVERCLAIM_RE.search(assertive)
    if match:
        out.append(
            Violation(
                rule="ast05-mitigation-overclaim",
                message=(
                    "claims the AST05 mitigations describe what this tool does. "
                    "Of six, SkillWatch covers one and part of two."
                ),
                excerpt=match.group(0),
                source=source,
            )
        )

    # Rule 5 — OWASP's "Rescan continuously" must not be reworded to ours.
    match = REWORDED_CONTINUOUS_RE.search(assertive)
    if match:
        out.append(
            Violation(
                rule="owasp-continuous-reworded",
                message=(
                    "restates OWASP's 'Rescan continuously' mitigation in this "
                    "project's own vocabulary. Quote the source's word and note the "
                    "divergence explicitly."
                ),
                excerpt=match.group(0),
                source=source,
            )
        )

    return out


def format_violations(violations: list[Violation]) -> str:
    """Render violations for a terminal, one per line."""
    if not violations:
        return "No claim violations."
    lines = [f"{len(violations)} claim violation(s):"]
    for v in violations:
        lines.append(f"  [{v.rule}] {v.source}: {v.message}")
        if v.excerpt:
            lines.append(f"      excerpt: {v.excerpt!r}")
    return "\n".join(lines)
