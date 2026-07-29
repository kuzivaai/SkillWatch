# ADR-0001 — Two-plane architecture: local learning + maintainer-side Observatory

- **Status:** Proposed
- **Date:** 2026-07-12
- **Deciders:** Kuziva Muzondo (maintainer)
- **Supersedes:** nothing. Complements `docs/ARCHITECTURE.md`, `docs/LEDGER.md`.

## Context

Two product asks arrived together:

1. Make SkillWatch **learn from usage and improve continuously**.
2. Use **Apify** to deepen what it can do.

Taken at face value, both break the project's founding promise and its settled
constraints:

- The README's headline trust claim is *"It runs on your machine and sends
  nothing… Platform scanners often upload your skill code to their servers…
  a different trust model."* Usage telemetry (learning "from usage") and routing
  a user's watched URLs through Apify's cloud both **violate that promise** and
  turn SkillWatch into the category it defines itself against.
- Settled constraints (`CLAUDE.md`): **no ML/LLM detection**, **no telemetry**,
  **periodic not continuous**. "Learn from usage" naively implies all three.

So the naive version of these asks does not strengthen the moat — it destroys it.

## Framing: requisite variety (why the current design is already right)

Ashby's **Law of Requisite Variety** (the first law of cybernetics): a regulator
needs at least as much variety as the disturbances it must absorb. There are two
ways to obtain it:

- **Amplify the regulator's variety** — more patterns, ML, semantic detection.
  Against a semantic adversary this is an arms race SkillWatch cannot win, and has
  honestly documented as evadable. Rejected, by design.
- **Attenuate the disturbance's variety** — reframe so the attacker's cleverness
  becomes irrelevant. Hashing content and detecting *change*, then anchoring it in
  a verifiable ledger, collapses the entire space of "malicious payload" to one
  bit: *did the approved bytes change?* This has requisite variety over the whole
  attack class. **This is the moat** (the ledger + anchoring already built).

This ADR extends attenuation — **without** re-entering the detection arms race and
**without** breaking local-only.

## Decision

Split the system into two planes with a **one-directional** boundary.

### Plane 1 — the tool on the user's machine (local-only stays sacred)

- Never phones home; never routes fetches through third-party clouds.
- "Learning" is realised two ways, both on-device and non-ML:
  - **Local false-positive adaptation** — the tool tunes its own noise from the
    user's own dismiss/confirm decisions, stored locally (see spec Plane 1 §B).
  - **Signed pattern updates** — `skillwatch update` pulls a public, versioned,
    **signed** ruleset and applies it. The detector improves every release; the
    user still sends nothing (see spec Plane 1 §A). This is how gitleaks/YARA/AV
    improve — the honest reading of "improve all the time".
- Optional **local multi-persona fetch** (cloaking-lite): fetch each watched URL
  under several User-Agent/Accept-Language personas *from the user's machine* and
  flag content that varies by requester. Still only contacts URLs the user asked
  to watch — no new trust cost.

### Plane 2 — maintainer-side Observatory (where Apify is used)

- Runs on maintainer infrastructure, **never bundled into the user's tool** and
  **never receives user data**.
- Apify-powered: discover skills/MCP tools + their external URLs, watch those URLs
  with **geo/residential-proxy variety** to catch cloaking a single local fetch
  misses, and accumulate a longitudinal, anchored corpus of real content changes.
- Two payoffs: it **feeds Plane 1's signed pattern updates** from *real observed
  attacks*, and it **is a compounding data-moat asset** — a public "Observatory"
  report ("N skills watched, M swaps caught") that doubles as the project's
  missing demand signal (see spec Plane 2).

### The invariant that makes this safe

Information flows **Plane 2 → Plane 1 only**, through a public, signed, auditable
pattern feed. There is **no user → server channel, ever.** A user's tool and the
Observatory never exchange private data in either direction. If a change would
create a user→server channel, it is out of bounds by definition.

## Consequences

**Positive**
- The tool learns and improves continuously with **zero telemetry** — promise intact.
- The Observatory builds a compounding dataset competitors don't have, and produces
  the exact publishable artifact the binding constraint (0 users) needs.
- Requisite variety is honoured by attenuation at ecosystem scale, not an arms race.

**Negative / costs (owned explicitly)**
- Apify is **paid**; the Observatory is a real, ongoing cost centre. Keep the MVP tiny.
- Positioning shifts from "pure local tool" to "local tool **+** maintainer-run
  observatory." Legitimate, but a deliberate choice, and the two planes must stay
  cleanly separated and clearly documented.
- Maintainer burden: the pattern feed needs a **named owner and cadence** (this also
  discharges readiness condition 3 in `DECISION.md`).

## Alternatives rejected

- **Usage telemetry / phone-home learning** — kills the trust moat. Rejected.
- **Route user fetches through Apify** — kills local-only. Rejected. Apify is
  Plane-2-only.
- **ML/LLM classifier in the tool** — violates a settled constraint and the trust
  model; an arms race besides. Rejected.
- **Do nothing** — viable; leaves the moat thin against a well-funded field.

## Honesty notes

- This is a head-start plus a compounding dataset, **not** an unbreachable moat.
  Snyk could build an observatory too. Keep saying "a combination I haven't seen
  elsewhere," never "the only tool."
- Everything here is **downstream of distribution** except the Observatory, which is
  the most distribution-relevant piece. Sequence: ship v0.3.0 → Observatory MVP that
  yields one publishable catch → grow. Do not build the full pipeline pre-launch.
