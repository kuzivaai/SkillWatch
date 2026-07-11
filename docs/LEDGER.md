# Verifiable content ledger

SkillWatch keeps an append-only, hash-chained record of what every monitored URL
served and when. This document describes exactly how it is built, what `verify`
checks, what the guarantee is and is not, and how to re-verify an exported ledger
yourself without trusting SkillWatch.

## Why it exists

The snapshot cache keeps only the most recent 50 versions per URL, to bound disk
use. That is fine for diffing a change against the previous state, but it means
older history is discarded. The ledger keeps a tiny hash entry for **every**
observation, permanently, so you retain a complete and tamper-evident history of
what a page served over time — the record you need to show *when* a bait-and-switch
happened, not just that the latest version differs.

## What is recorded

One ledger entry is appended for every successful observation (an errored fetch
served no content, so it is not part of the "what did this URL serve" record).
Each entry commits to four facts:

| Field | Meaning |
|---|---|
| `url` | The URL observed |
| `fetched_at` | When it was fetched (the snapshot's recorded time) |
| `content_hash` | SHA-256 of the extracted text |
| `status_code` | The HTTP status, or empty |

## The hash construction

Defined in [`skillwatch/ledger.py`](../skillwatch/ledger.py). `SPEC_VERSION = 1`.

```
GENESIS_HASH = "0" * 64                                   # prev_hash of the first entry

entry_hash  = sha256( json([url, fetched_at, content_hash, status_code]) )
chain_hash  = sha256( prev_hash || entry_hash )
```

- Fields are encoded as a compact JSON array (`json.dumps(..., separators=(",",
  ":"))`) before hashing. JSON escapes any separator inside a field, so two
  different tuples can never collide — a plain delimiter join is ambiguous
  (`"a\nX","Y"` and `"a","X\nY"` would render identically). `status_code` of
  `None` becomes JSON `null`.
- The first entry's `prev_hash` is `GENESIS_HASH`; every later entry's `prev_hash`
  is the previous entry's `chain_hash`. The entries therefore form a single chain,
  and the last entry's `chain_hash` (the **head**) commits to the entire history.

## What `skillwatch verify` checks

`verify` recomputes the chain from the stored facts and compares it to what is
recorded. For each entry, in `seq` order:

1. **Link check** — its `prev_hash` must equal the previous entry's `chain_hash`
   (the first must be `GENESIS_HASH`). A failure means an entry was deleted,
   reordered, or inserted.
2. **Content check** — its `chain_hash` must equal `chain_hash(prev_hash,
   entry_hash(facts))`. A failure means a past record's facts were altered.

The first entry that fails either check is reported by `seq`, and `verify` exits
`1`. A clean ledger exits `0`. An empty ledger is vacuously valid.

Because any edit to entry *N* changes its `chain_hash`, it also breaks entry
*N+1*'s link check — so a single naive edit cannot hide.

## Honest scope — what this is and is not

- **It is** tamper-*evidence* and independent verifiability. Accidental
  corruption, a naive manual edit, a deleted row, or a reordering is detected on
  the next `verify`, and anyone can re-check an exported ledger without access to
  your machine.
- **On its own, a local chain is not tamper-*proof*.** An attacker with write
  access to your database can edit an entry and then recompute every subsequent
  `chain_hash`, producing a chain that plain `verify` accepts. Nothing *inside*
  the chain pins its history, so the chain alone cannot prevent a full rewrite.

## Anchoring your history

The fix for that residual gap does not need any network service. The **head**
(the last entry's `chain_hash`) commits to the entire history, so:

1. Run `skillwatch verify`. It prints `Current head: <hash>`.
2. **Publish that head somewhere you do not control** — a git commit, a public
   note, a tweet, an [RFC 3161](https://www.rfc-editor.org/rfc/rfc3161) timestamp,
   [Sigstore Rekor](https://docs.sigstore.dev/logging/overview/), or
   [OpenTimestamps](https://opentimestamps.org/). Only a 64-character hash leaves
   your machine — never page content, never anything identifying you.
3. Later, run `skillwatch verify --against <that head>`.

Because a published head cannot be altered after the fact, this makes all history
*up to that head* tamper-proof: if anyone rewrites an earlier entry — even
recomputing the whole chain so plain `verify` passes — the head changes, the
published one is no longer in the chain, and `verify --against` reports
`DIVERGED` and exits `1`. This is demonstrated in
[`tests/test_ledger.py`](../tests/test_ledger.py) (`TestVerifyAgainstAnchor`).

## Automatic anchoring: `skillwatch anchor`

Publishing the head by hand is the zero-dependency path. For a stronger,
automated anchor, `skillwatch anchor` obtains a signed **RFC 3161 timestamp
token** for the current head from a public Time-Stamp Authority (freeTSA.org by
default). The TSA's signature cannot be forged, so the token is proof that the
head existed at the attested time.

```bash
pip install 'skillwatch[anchor]'          # optional extra: rfc3161-client + cryptography
skillwatch anchor                         # RFC 3161 timestamp via the default TSA (freeTSA.org)
skillwatch anchor --out head.tsr          # also save the token to preserve/publish
skillwatch anchor --tsa https://my.tsa/   # use a different RFC 3161 authority
skillwatch anchor --method git --repo .   # commit the head to a git repo (no TSA, no extra)
skillwatch verify                         # now auto-checks every recorded anchor
```

Two backends, so you are not tied to one authority:

- **`rfc3161`** (default) gets a signed timestamp token whose signature cannot be
  forged. It depends on a Time-Stamp Authority being reachable at anchor time
  (only freeTSA.org currently parses cleanly with `rfc3161-client`); verification
  is always offline. Needs the `[anchor]` extra.
- **`git`** appends the head to `.skillwatch-anchors.log` and commits it. Push
  that repo to GitHub (or any remote) and the commit is an independent,
  timestamped record that depends on no timestamp authority and needs no extra
  dependency. A rewrite of anchored history is caught by `verify` (the head
  leaves the chain), and the pushed commit is your out-of-band proof of when.

Anchors are stored in an `anchors` table (head, method, the token, the attested
time). `skillwatch verify` then automatically, for every recorded anchor, (a)
confirms the anchored head is still in the chain and (b) cryptographically
verifies the token against that head — so a rewrite of anchored history is caught
without any manual `--against`. Verification uses freeTSA's CA certificate,
bundled in the package, so it works offline.

Only a hash ever leaves the machine — never page content or anything identifying
you. The anchoring crypto is an **optional** extra; the core tool stays
dependency-light and fully offline, and `verify` still runs (reporting anchors as
recorded-but-not-cryptographically-checked) if the extra is not installed.
`SPEC_VERSION` lets the hash construction evolve without invalidating tokens.

## Re-verify an export yourself

`skillwatch ledger --export ledger.json` writes the whole ledger as portable JSON:

```json
{ "skillwatch_ledger_version": 1, "entries": [ { "seq": 1, "url": "...", ... } ] }
```

You can confirm it with SkillWatch's own public function — no database, no trust
in the running tool:

```python
import json
from skillwatch.ledger import verify_chain

payload = json.load(open("ledger.json"))
result = verify_chain(payload["entries"])
print(result.ok, result.entries, result.broken_seq)
```

Or reimplement the two-line hash construction above in any language and check it
independently. That is the point: the record does not require trusting SkillWatch.
