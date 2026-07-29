# Spec — Plane 2: maintainer-side Observatory (Apify)

Implements the Plane-2 half of [ADR-0001](../adr/0001-two-plane-architecture.md).
Runs on **maintainer** infrastructure. It **never** ships in the user's tool and
**never** receives user data. It only ever touches **public** skill URLs — this is
security research on public data.

## Purpose

1. Watch skills/MCP tools and the external URLs they point to, at ecosystem scale,
   with enough fetch **variety** to catch cloaking (requisite-variety
   response-matching, ADR-0001).
2. Turn confirmed real content-swaps into **signed pattern-feed updates** for Plane 1.
3. Publish a longitudinal **Observatory report** — the compounding data moat and the
   project's missing demand signal.

## Pipeline (scheduled, e.g. weekly)

```
discover → watch (multi-geo) → detect change → confirm → {feed update, ledger, report}
```

### 1. Discover (prefer free over Apify)

- **Primary (free):** GitHub REST/Search API for `SKILL.md`, MCP config files, and
  known skill repos; the `awesome-agent-skills` lists; MCP registries; and the
  ClawHavoc campaign's compromised-skill list (per Orca's research). **Do not pay
  Apify for discovery that the free GitHub API already does.**
- **Optional (paid):** Apify `ryanclinton/github-repo-search` (has a built-in
  `compareToPreviousRun` change flag). Priced at **$0.15/repo** — only worthwhile for
  breadth the API can't reach; flag the cost before enabling.
- Extract external URLs with the existing `skillwatch.parser` (same code the tool uses).

### 2. Watch with geo/persona variety (this is where Apify earns its place)

For each external URL, fetch through **Apify `apify/website-content-crawler`**
(id `aYG0l9s7dbB7j3gbS`, **FREE actor**), which supports `proxyConfiguration` and
`customHttpHeaders`. Run each URL under several personas:

- residential proxy in ≥2 countries (`useApifyProxy: true`,
  `apifyProxyGroups: ["RESIDENTIAL"]`, `apifyProxyCountry`),
- browser vs agent-like vs bot User-Agents, varying `Accept-Language`.

If the server returns materially different content across personas → **cloaking**,
which a single local fetch (Plane 1) structurally cannot see. Residential geo proxies
are Apify's genuine, hard-to-DIY value here.

### 3. Detect + confirm

- Hash + diff each observation; when content changes vs the last snapshot, run the
  **existing `skillwatch.detector`** (same 13 flags / canonicalisation) — no new
  detection engine, no ML.
- Human-in-the-loop confirmation before anything becomes a pattern (this is the
  "named maintenance owner + cadence" that `DECISION.md` requires).

### 4. Corpus + ledger

- Append every observation to a longitudinal store and **anchor it** with the
  existing `skillwatch.anchoring` (git or rfc3161) so the Observatory's own history
  is tamper-evident — the same verifiability guarantee the tool gives users.

### 5. Feed + report

- Distil confirmed swaps into new/updated rules, sign, publish to the Plane-1 feed
  (with `provenance` pointing back to the corpus event).
- Publish a static **Observatory report**: skills watched, changes seen, cloaking
  cases, confirmed malicious swaps — with links to the anchored evidence.

## Cost model (honest, rough)

- `website-content-crawler` is a **free actor**; you pay only proxy/compute. A
  residential fetch is on the order of a fraction of a US-cent.
- MVP scale — ~50 URLs × 3 personas × weekly ≈ 600 fetches/week — is a few dollars a
  month at most. `github-repo-search` at $0.15/repo is the line item to watch; keep
  discovery on the free GitHub API.
- This is a **real, ongoing cost centre.** Keep the MVP tiny; scale only after the
  first published catch proves demand.

## Prototype

`prototypes/cloaking_prototype.py` (+ `prototypes/test_cloaking_prototype.py`) — real,
tested code, **not wired into the shipped tool**:

- `Persona`, `DEFAULT_PERSONAS` — UA/Accept-Language/country personas.
- `compare_personas(results)` → `CloakingResult` — backend-agnostic comparison
  (distinct-content grouping + min pairwise similarity). Unit-tested for free with
  synthetic clean/cloaking fixtures.
- `LocalBackend` — multi-UA fetch from this machine (free; Plane-1 cloaking-lite).
- `ApifyBackend` — fetches via `website-content-crawler` with residential geo proxies
  and per-persona headers. **Implemented but not fired** in tests or here; needs
  `APIFY_TOKEN` and an explicit opt-in (it spends credits).

Run the free local demo:

```bash
python prototypes/cloaking_prototype.py https://example.com
```

Run the paid Apify path (maintainer, explicit):

```bash
APIFY_TOKEN=... python prototypes/cloaking_prototype.py https://example.com --backend apify --country US --country DE
```

## Invariants (restated)

- Public skill URLs only; never user data; **Plane 2 → Plane 1 one-directional feed**.
- Reuse `parser`, `detector`, `anchoring` — no forked detection logic, no ML.

## Sequencing

After v0.3.0 ships. MVP = a handful of URLs + one cloaking pass + **one published
"we caught X"** artifact. That artifact is the point — it is the demand signal.
