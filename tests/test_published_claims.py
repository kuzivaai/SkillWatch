"""Guards on claims this project makes about other people's work.

The failure this exists to catch is not a typo. It is a chain: a primary source
says something precise, a secondary source compresses it and loses the scope or
the quantifier, and we repeat the compression on a page users read.

That happened. Trail of Bits wrote that it "took us less than an hour to conceive
and implement three of the four malicious skills". OWASP's incident timeline
rendered it as "every public skill scanner tested ... is bypassed in under an
hour" — the hour moved from *building three of four attacks* to *bypassing
scanners*, and the fourth attack that took a few hours disappeared. The README
then repeated OWASP. Two hops, two distortions.

A test cannot check whether a paraphrase is faithful; that needs a human with the
source open. What it *can* check is the mechanical precondition for anyone ever
noticing: that a cited finding on a public surface is accompanied by a link to
where it came from. An unsourced attribution cannot be audited by a reader, and
in practice is not audited by us either.

Scope note: these tests read the repository's own published surfaces. They do not
fetch anything. Keeping them offline means they run in CI and on a plane, and it
means they never fail because someone else's site is down.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Surfaces a user or an indexer actually reads.
PUBLIC_SURFACES = [
    "README.md",
    "docs/llms.txt",
    "docs/index.html",
    "SHIP-READINESS.md",
]

# Named third parties whose findings this project cites. Attributing work to a
# named outside party is exactly the case that needs a source link: the reader
# has no way to check it otherwise, and we have repeatedly got the details wrong
# when working from memory or from someone else's summary.
ATTRIBUTED_SOURCES = {
    "Trail of Bits": "blog.trailofbits.com",
    "OWASP": "owasp.org",
    "SIGIL": "arxiv.org",
    "Cloud Security Alliance": "cloudsecurityalliance.org",
}

URL_RE = re.compile(r"https?://[^\s)>\]\"']+")

# Correcting a bad claim requires naming it. A first draft of the negative checks
# below could not tell "the README asserts X" from "the README quotes X in order
# to retract it", so it failed on the very corrections it was written to enforce.
#
# The invariant that actually matters is that the surface does not *assert* the
# compressed claim. Quoting it, marked as wrong, is not merely allowed — it is
# how a reader learns the correction happened at all.
#
# So the negative checks run against assertive text only: blockquotes and
# explicitly-marked retraction sentences are stripped first. This is deliberately
# narrow. A future session that reintroduces the claim as a plain assertion still
# fails, which is verified by running these tests against the pre-correction
# README — see the commit that introduced this file.
RETRACTION_MARKERS = (
    "earlier version of this readme",
    "an earlier version",
    "earlier draft",
    "corrected here",
    "corrected above",
    "is corrected",
    "gets garbled",
    "get garbled",
)


def _read(rel: str) -> str:
    """Read a public surface, failing loudly if it is missing.

    Deliberately not `pytest.skip`. A first draft skipped when the file was
    absent, which meant deleting README.md would turn every guard in this file
    green. That is the same fail-open shape the dependency auditor had — an
    absent input reported as "fine" rather than "cannot check". These four files
    are tracked and required; if one is gone, that is the finding.
    """
    path = REPO_ROOT / rel
    assert path.exists(), (
        f"{rel} is missing. It is a tracked public surface these guards depend on; "
        f"its absence is a failure, not a reason to skip."
    )
    return path.read_text(encoding="utf-8")


def _assertive_text(markdown: str) -> str:
    """Return only the prose that speaks in the document's own voice.

    Drops markdown blockquotes (someone else's words) and any sentence carrying
    an explicit retraction marker (our words about a past error).
    """
    kept_lines = [ln for ln in markdown.splitlines() if not ln.lstrip().startswith(">")]
    flattened = " ".join(kept_lines)
    sentences = re.split(r"(?<=[.!?])\s+", flattened)
    return " ".join(s for s in sentences if not any(m in s.lower() for m in RETRACTION_MARKERS))


def _surfaces_mentioning(needle: str) -> list[tuple[str, str]]:
    out = []
    for rel in PUBLIC_SURFACES:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if needle in text:
            out.append((rel, text))
    return out


class TestCitedFindingsCarryASource:
    """Naming an outside party on a public surface requires linking to them."""

    @pytest.mark.parametrize(("name", "domain"), sorted(ATTRIBUTED_SOURCES.items()))
    def test_attributed_party_is_linked_on_every_surface_naming_it(
        self, name: str, domain: str
    ) -> None:
        for rel, text in _surfaces_mentioning(name):
            urls = URL_RE.findall(text)
            assert any(domain in u for u in urls), (
                f"{rel} attributes a finding to {name!r} but links nowhere on "
                f"{domain}. A reader cannot check it and neither can we. "
                f"Add the primary source URL."
            )


class TestTrailOfBitsScopeAndQuantifier:
    """The specific distortion that prompted this file, pinned so it cannot return.

    These assert on *our* text, not on Trail of Bits'. The source sentence is
    reproduced in CLAUDE.md and in the commit that introduced this file.
    """

    def test_readme_does_not_repeat_the_compressed_claim(self) -> None:
        readme = _assertive_text(_read("README.md"))
        # OWASP's compression moved the hour onto the scanners. Ours must not.
        offending = re.compile(
            r"scanner[s]?[^.\n]{0,80}(?:is|was|were|are)\s+bypassed\s+in\s+under\s+an\s+hour",
            re.IGNORECASE,
        )
        match = offending.search(readme)
        assert match is None, (
            "README attaches 'under an hour' to bypassing scanners. The source "
            "attaches it to conceiving and implementing three of four attacks; "
            "the fourth took a few hours. Found: " + repr(match.group(0) if match else "")
        )

    def test_readme_states_the_scope_is_the_scanners_tested(self) -> None:
        readme = _read("README.md")
        if "Trail of Bits" not in readme:
            pytest.skip("README no longer cites Trail of Bits")
        assert "three of the four" in readme, (
            "README cites Trail of Bits without the source's own quantifier "
            "('three of the four malicious skills'). Scope and quantifier travel "
            "with the finding."
        )


class TestOwaspMitigationClaim:
    """AST05 lists six mitigations. We cover one and part of two."""

    def test_readme_does_not_claim_the_mitigations_describe_this_tool(self) -> None:
        readme = _assertive_text(_read("README.md"))
        overclaim = re.compile(
            r"mitigations[^.\n]{0,60}describe what this tool\s+does", re.IGNORECASE
        )
        assert overclaim.search(readme) is None, (
            "README claims the AST05 mitigations describe what this tool does. "
            "Of six, SkillWatch covers one and part of two."
        )

    def test_readme_does_not_reword_owasps_continuous_mitigation(self) -> None:
        """OWASP's mitigation 6 is 'Rescan continuously'.

        This project is periodic by design and must never quietly restate that
        mitigation as 'repeated' or 'periodic' rescanning to make the fit look
        cleaner than it is. Quote OWASP's word; state ours separately.
        """
        readme = _assertive_text(_read("README.md"))
        reworded = re.compile(
            r"(?:mitigations?|lists?)[^.\n]{0,120}(?:repeated|periodic)\s+rescanning",
            re.IGNORECASE,
        )
        assert reworded.search(readme) is None, (
            "README restates OWASP's 'Rescan continuously' mitigation in this "
            "project's own vocabulary. Quote the source's word and note the "
            "divergence explicitly."
        )
