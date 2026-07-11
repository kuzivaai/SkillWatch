"""Verifiable content ledger: the hash-chain spec and chain verification.

The ledger is an append-only, never-pruned record of what each monitored URL
served and when. Each entry commits to the observation facts (URL, fetch time,
content hash, HTTP status) and links to the previous entry, so the whole history
forms a hash chain. Editing, reordering, or deleting any past entry breaks the
chain from that point and is caught by :func:`verify_chain`.

This module is pure (no I/O). The same :func:`verify_chain` verifies both the
live SQLite ledger and an exported JSON ledger, so anyone can independently
re-verify a record SkillWatch produced.

Honest scope: a purely local chain proves *integrity* and enables *independent
re-verification*. It does NOT defend against a motivated local attacker who
recomputes the entire chain after an edit. Binding the chain head to an external
public log (RFC 3161 / Sigstore Rekor) removes that caveat and is a separate,
documented increment. The hash spec below is versioned so anchoring can build on
it without breaking existing exports.
"""

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass

# Bump only if the hash construction below changes; exported ledgers record it.
SPEC_VERSION = 1

# The prev_hash of the first entry. Fixed-width and obviously a genesis marker.
GENESIS_HASH = "0" * 64


def entry_hash(url: str, fetched_at: str, content_hash: str, status_code: int | None) -> str:
    """Hash the observation facts for one ledger entry.

    The fields are encoded as a compact JSON array before hashing. JSON escapes
    any separator inside a field, so two different field tuples can never render
    to the same byte string (a plain delimiter join is ambiguous: "a\\nX","Y"
    and "a","X\\nY" would collide). ``status_code`` of ``None`` becomes JSON null.
    """
    payload = json.dumps(
        [url, fetched_at, content_hash, status_code],
        ensure_ascii=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def chain_hash(prev_hash: str, this_entry_hash: str) -> str:
    """Link an entry to its predecessor: sha256(prev_hash || entry_hash)."""
    return hashlib.sha256((prev_hash + this_entry_hash).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class LedgerVerification:
    """Result of verifying a ledger chain."""

    ok: bool
    entries: int
    broken_seq: int | None = None
    reason: str | None = None
    # The chain head (last entry's chain_hash) on a valid, non-empty chain.
    # Publish it externally to anchor history; None if empty or broken.
    head: str | None = None


def verify_stream(entries: Iterable[dict]) -> LedgerVerification:
    """Verify entries supplied in ascending ``seq`` order, in O(1) memory.

    Unlike :func:`verify_chain`, this does NOT sort — the caller guarantees seq
    order (a SQL ``ORDER BY seq`` cursor does). Use this to verify a very large
    ledger without materialising it. Each dict needs keys ``seq``, ``url``,
    ``fetched_at``, ``content_hash``, ``status_code``, ``prev_hash`` and
    ``chain_hash``. Returns the first ``seq`` at which the chain breaks.
    """
    prev = GENESIS_HASH
    count = 0
    head: str | None = None

    for e in entries:
        count += 1
        expected_entry = entry_hash(
            e["url"], e["fetched_at"], e["content_hash"], e["status_code"]
        )
        expected_chain = chain_hash(e["prev_hash"], expected_entry)

        if e["prev_hash"] != prev:
            return LedgerVerification(
                ok=False,
                entries=count,
                broken_seq=e["seq"],
                reason="chain link does not match the previous entry "
                "(an entry was deleted, reordered, or inserted)",
            )
        if e["chain_hash"] != expected_chain:
            return LedgerVerification(
                ok=False,
                entries=count,
                broken_seq=e["seq"],
                reason="recorded hash does not match the entry contents "
                "(a past record was altered)",
            )
        prev = e["chain_hash"]
        head = e["chain_hash"]

    return LedgerVerification(ok=True, entries=count, head=head)


def verify_chain(entries: list[dict]) -> LedgerVerification:
    """Verify a ledger chain from a list in any order.

    Sorts by ``seq`` ascending (so an export in any order still verifies), then
    delegates to :func:`verify_stream`. For a large live ledger, prefer feeding
    an ordered cursor straight to ``verify_stream`` to avoid loading it all.
    """
    return verify_stream(sorted(entries, key=lambda e: e["seq"]))
