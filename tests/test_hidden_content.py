"""Behavioural test for `hidden_content`, one row per hiding technique.

This began as an ad-hoc probe script run by hand in three separate sessions. Each
time it found something nobody had recorded — that the check was case-sensitive,
that it could not see `<style>` blocks, that stylesheet hiding was the largest gap
in practice. A finding that has to be rediscovered by hand every session is not
guarded; it is remembered. So the probe is a test.

Bucket classifications and their reasoning are in
`docs/HIDING-TECHNIQUE-TAXONOMY.md`. In short:

  a — conceals from a human, stays in the text an agent ingests. Must flag.
  b — accessibility idiom (`.sr-only`). Deliberately must NOT flag; flagging the
      canonical screen-reader pattern fires on well-built sites and spends the
      benign false-positive budget on correct behaviour.
  c — inverse of the threat (`aria-hidden` hides from machines, not humans).
      Must NOT flag.
  x — out of reach by hard boundary, not by effort. Resolving an external
      stylesheet means fetching a URL the user never specified.
"""
from __future__ import annotations

import pytest
from bs4 import BeautifulSoup

from skillwatch.detector import _extract_hidden_texts

PAYLOAD = "SECRET-PAYLOAD-TEXT"

# (label, bucket, html, should_be_detected)
TECHNIQUES = [
    # --- bucket (a): must be detected ---
    ("inline display:none", "a", f'<p style="display:none">{PAYLOAD}</p>', True),
    ("inline display: none", "a", f'<p style="display: none">{PAYLOAD}</p>', True),
    ("inline visibility:hidden", "a", f'<p style="visibility:hidden">{PAYLOAD}</p>', True),
    ("UPPERCASE DISPLAY:NONE", "a", f'<p style="DISPLAY:NONE">{PAYLOAD}</p>', True),
    ("mixed-case Display:None", "a", f'<p style="Display: None">{PAYLOAD}</p>', True),
    # Moved to (b) 2026-07-29: WebAIM calls this the RECOMMENDED .sr-only
    # implementation, so flagging it fires on correct accessibility markup.
    (
        "off-screen position",
        "b",
        f'<p style="position:absolute;left:-9999px">{PAYLOAD}</p>',
        False,
    ),
    ("opacity:0", "a", f'<p style="opacity:0">{PAYLOAD}</p>', True),
    ("font-size:0", "a", f'<p style="font-size:0">{PAYLOAD}</p>', True),
    (
        "height:0;overflow:hidden",
        "a",
        f'<p style="height:0;overflow:hidden">{PAYLOAD}</p>',
        True,
    ),
    # Moved to (b) 2026-07-29: 111/201 real pages (55.2%) carry it. It is the
    # platform's UI-state primitive, not a concealment technique.
    ("HTML hidden attribute", "b", f"<p hidden>{PAYLOAD}</p>", False),
    (
        "<style> block rule",
        "a",
        f'<style>.x{{display:none}}</style><p class="x">{PAYLOAD}</p>',
        True,
    ),
    # --- bucket (b): accessibility idiom, must NOT be detected ---
    # inset(50%) is the value the canonical WebAIM ruleset actually uses;
    # the taxonomy previously named inset(100%), which it does not use.
    ("clip-path inset(50%)", "b", f'<p style="clip-path:inset(50%)">{PAYLOAD}</p>', False),
    ("text-indent:-9999px", "b", f'<p style="text-indent:-9999px">{PAYLOAD}</p>', False),
    # --- bucket (c): inverse of the threat, must NOT be detected ---
    ("aria-hidden", "c", f'<p aria-hidden="true">{PAYLOAD}</p>', False),
    # --- bucket (x): out of reach by boundary ---
    (
        "external stylesheet",
        "x",
        f'<link rel="stylesheet" href="a.css"><p class="x">{PAYLOAD}</p>',
        False,
    ),
]


def _detected(html: str) -> bool:
    return bool(_extract_hidden_texts(BeautifulSoup(html, "html.parser")))


@pytest.mark.parametrize(
    ("label", "bucket", "html", "expected"),
    TECHNIQUES,
    ids=[t[0] for t in TECHNIQUES],
)
def test_technique_detection_matches_its_bucket(
    label: str, bucket: str, html: str, expected: bool
) -> None:
    got = _detected(html)
    if expected:
        assert got, (
            f"bucket ({bucket}) technique {label!r} conceals content from a human "
            f"while leaving it in the text an agent ingests, and was not flagged."
        )
    else:
        reason = {
            "b": "is a canonical .sr-only accessibility idiom and flagging it "
            "spends the false-positive budget on correct behaviour",
            "c": "hides content from assistive technology while leaving it "
            "visually present — the inverse of the threat",
            "x": "is out of reach by hard boundary: resolving it means fetching "
            "a URL the user never specified",
        }[bucket]
        assert not got, f"bucket ({bucket}) technique {label!r} {reason}, but was flagged."


class TestBoundaryIsDocumentedNotAccidental:
    """External stylesheets are excluded by policy. Pin that it is deliberate."""

    def test_external_stylesheet_boundary_is_in_the_docstring(self) -> None:
        doc = _extract_hidden_texts.__doc__ or ""
        assert "external" in doc.lower(), (
            "the docstring must state that external stylesheets are out of scope, "
            "so a later reader does not mistake the gap for an oversight"
        )


class TestHiddenTextIsActuallyReturned:
    """Detecting the element is not enough; the concealed text must be recoverable."""

    def test_returns_the_concealed_text(self) -> None:
        found = _extract_hidden_texts(
            BeautifulSoup(f'<p style="opacity:0">{PAYLOAD}</p>', "html.parser")
        )
        assert PAYLOAD in " ".join(found)

    def test_empty_hidden_element_yields_nothing(self) -> None:
        assert _extract_hidden_texts(
            BeautifulSoup('<p style="display:none"></p>', "html.parser")
        ) == set()
