# SkillWatch business and operations dossier

**Status:** current operating plan, not a claim of commercial readiness

**Audience:** maintainer, engineering contributors, security reviewers,
design-partner participants and potential buyers

**Last updated:** 2026-08-01

## Executive summary

SkillWatch is a local command-line tool that periodically fetches
user-specified public URLs, records a local baseline, compares later content,
identifies selected suspicious changes, and maintains a tamper-evident local
observation ledger.

It is mechanically ready for a controlled design-partner pilot. It is not
proven to have product-market fit, commercial demand, human trust, retention,
payment value, or a durable competitive moat.

The recommended business posture is **evidence-first HOLD**:

1. Run a small, qualified design-partner pilot.
2. Measure whether evidence changes real operational decisions.
3. Do not build an integration until two independent qualified participants
   request the same kind of workflow destination and identify its owner.
4. Continue standalone development only if participants repeatedly use the
   tool and obtain decision value that generic monitors do not provide.
5. Otherwise pivot toward assurance services or pause development.

The product does **not** learn autonomously across users. It has no telemetry
and no user-to-server data channel. Adding such learning would require a new
privacy, consent, security and data-governance model, so it is outside the
current product boundary.

## 1. What the product is

### Plain-language description

SkillWatch watches external instructions that an AI skill, MCP configuration or
similar asset depends on. It stores what it saw locally and later tells the
operator when the fetched content changed or contains selected warning signs.

### Current capabilities

- Extract references from supported local files.
- Reject private, local and reserved network addresses.
- Fetch approved public URLs.
- Store a local first observation, called a **baseline**.
- Compare later observations with the baseline.
- Report selected suspicious patterns, such as newly introduced executable
  commands, credential references, new domains and selected hidden content.
- Record observations in a hash-linked **ledger** (a sequence where each entry
  includes evidence of the previous entry, making later rewriting detectable).
- Verify or export the local ledger.
- Produce machine-readable output formats including JSON and SARIF where
  supported.

### Explicit boundaries

- Local-only operation.
- No telemetry (automatic usage reporting).
- No machine-learning or large-language-model detection.
- Periodic operation, not continuous monitoring.
- No user-to-server data channel.
- Outbound traffic is limited to URLs explicitly supplied by the user.
- Regex and rule-based detection is triage, not proof of compromise.
- It does not establish publisher identity or guarantee that content is safe.

## 2. Current evidence status

### Demonstrated

- Candidate installation and core CLI workflow in isolated environments.
- Baseline creation against a valid public URL.
- Repeated unchanged scan.
- Ledger verification and export.
- Clear failure for an all-rejected input file.
- 647 automated tests passing.
- 95.71% production-code coverage.
- Ruff, mypy, dependency-floor, release-claim, figure, capture and build gates.

### Unverified

- Human usability and trust.
- Retention and unprompted continued use.
- Demand, willingness to pay and purchase behavior.
- Provenance evidence changing a real decision.
- Superiority over generic monitors in a participant workflow.
- Organic-drift false-positive rate.
- Durable moat.

### Contradicted or not claimable

- “Commercially ready” is not supported.
- “Autonomously learning from all use” is false under the current architecture.
- “Comprehensive detection” is not supported.
- “Prevents prompt injection” is not supported.
- “ISO 27001 certified,” “NIST compliant,” or “OWASP SAMM compliant” would be
  false unless a separate qualified assessment established those claims.

## 3. Users, buyers and jobs

The **user** operates the workflow. The **buyer** controls budget or approval.
They may be the same person, but must not be assumed to be.

| Profile | User job | Possible buyer | Qualification | Disqualifier |
|---|---|---|---|---|
| Agent-security reviewer | Review mutable external references in deployed skills or MCP configurations | AppSec or AI-platform lead | A real asset, mutable reference and real review decision | Curiosity-only evaluation or no authority to act |
| Skill/MCP maintainer | Detect and explain upstream changes to referenced instructions | Project/platform owner | Repeated reference review has operational consequence | Immutable references or generic monitor fully satisfies need |
| Assurance consultant | Produce repeatable evidence of what changed and when | Consultancy principal or client assurance owner | Evidence enters client decisions | One-off assessment with no retention need |

## 4. Value proposition and falsification

### Hypothesis

SkillWatch may create value by combining:

1. reference discovery;
2. periodic change detection;
3. affected-context explanation; and
4. portable local evidence of what was observed and reviewed.

The combination is a **hypothesis**, not a proven moat.

### Evidence that would support continuation

- Qualified users install with limited intervention.
- They return for repeated scheduled runs.
- Genuine changes occur within the observation window.
- The diff or provenance changes an actual decision.
- Participants report that generic monitoring alone was insufficient.
- At least two independent participants request a concrete workflow integration.
- At least one participant demonstrates commercial follow-through, not only an
  interview statement.

### Evidence that would support a pivot

- Participants use exports and evidence in client assurance work but do not run
  the CLI independently: consider assurance/adaptation services.
- Participants value the evidence only inside an existing tool: consider a
  narrowly scoped integration after the two-request gate.
- Participants install but do not return, or generic monitors are sufficient:
  pause or stop standalone development.

## 5. Competitive position

### Honest comparison

Generic web-change monitors generally have stronger hosted operations,
rendering, filtering and convenience. General skill scanners have broader
security-analysis positioning and distribution.

SkillWatch’s credible differentiation hypothesis is narrower: local-first,
agent-reference-aware temporal evidence with a verifiable observation history.
That advantage is not yet demonstrated in user behavior.

### What is not a moat

- More regular expressions.
- Hashing by itself.
- A lockfile.
- Being first.
- High test count.
- Generic page monitoring.
- An Apache-2.0 licence by itself.
- A new signature protocol without adoption.

### Potential compounding assets

These could become harder to copy through use, but are currently unvalidated:

- organisation-specific reference and impact context;
- accepted review history;
- portable evidence interoperability;
- a lawful real-drift corpus;
- workflow knowledge;
- support and assurance reputation.

“Compounding” means usefulness may increase as legitimate use creates reusable
context. It does not mean collecting participant data secretly or training a
central model.

## 6. Business model options

| Route | Buyer | Value unit | Main risk | Decision rule |
|---|---|---|---|---|
| Standalone local CLI | AI-platform/AppSec operator | Decision-changing reviewed event | Extra installation and review burden | Continue only after repeated independent decision value |
| Workflow integration | Existing scanner/CI/registry owner | Evidence inserted into an existing approval decision | Building before a real request | No adapter before two concrete requests |
| Portable provenance | Assurance reviewer | Defensible evidence package | Diff may already be sufficient | Continue only when evidence changes a decision |
| Assurance/adaptation service | Consultant or assurance owner | Completed review, adaptation or evidence package | Labour does not scale | Require paid or procurement follow-through |
| Generic monitor | Operations buyer | Page-change alert | Mature substitutes | Rejected as primary route |
| Pause | Maintainer | Preserved capacity and reduced support burden | Opportunity cost | Default if pilot falsifies value |

No price is validated. Any future offer must distinguish:

- **stated preference:** what someone says they might pay;
- **commercial evidence:** a paid engagement, procurement step or signed
  commitment.

## 7. Pilot operating model

The canonical protocol is [DESIGN-PARTNER-PILOT.md](DESIGN-PARTNER-PILOT.md).
Participant execution uses:

- [participant runbook](pilot/PARTICIPANT-RUNBOOK.md);
- [maintainer checklist](pilot/MAINTAINER-CHECKLIST.md); and
- [manual observation template](pilot/OBSERVATION-TEMPLATE.csv).

### Pilot stages

1. Qualify the participant and separate user from buyer.
2. Record consent, redaction, access and deletion choices.
3. Supply an exact artefact and record its version and SHA-256 hash.
4. Install in a clean environment.
5. Add a participant-owned public reference.
6. Record the first useful baseline.
7. Run the agreed periodic schedule.
8. For a genuine change, review the diff first and provenance second.
9. Record the decision before and after each evidence type.
10. Pause maintainer support before the unprompted-use observation.
11. Record exit, deletion/retention and commercial follow-through.

### Pilot success measures

- installation completion;
- time to first useful baseline;
- commands and manual decisions;
- references discovered, missed and irrelevant;
- genuine changes;
- alerts reviewed;
- actionability;
- review time;
- benign-trigger burden;
- decision changed by diff or provenance;
- repeated and unprompted use;
- preference for change detection, impact mapping or provenance;
- integration requests with destination and workflow owner;
- stated willingness to pay, labelled as stated preference;
- actual commercial follow-through.

## 8. Operating procedures

### Release procedure

1. Freeze the intended change unit.
2. Run targeted tests and a full suite.
3. Run lint, type, dependency, claim, figure, capture and build gates.
4. Review the complete diff.
5. Confirm protected paths and dependency graph are unchanged unless explicitly
   authorised.
6. Update the continuity ledger.
7. Commit a coherent unit.
8. Fetch before push and confirm upstream has not moved.
9. Push normally; never force-push.
10. Wait for CI and inspect the actual deployed or published artefact before
    making public claims.

### Incident and defect procedure

1. Preserve the failing command and output.
2. Classify P0 (unsafe/blocking), P1 (materially misleading), P2 (friction),
   or P3 (preference).
3. Fix only reproduced P0/P1 defects in pilot units.
4. Add fail-before evidence where code changes.
5. Run a mutation or revert control.
6. Re-run the assurance gates.
7. Update the ledger with the opening and closing evidence.

### Participant support boundary

Maintainer support may clarify documented installation, diagnose a reproducible
defect and record an intervention. It must not operate the participant’s tool,
classify their alert, choose their security decision or manufacture a change.

### Data handling

SkillWatch itself stores local state. The pilot operator may manually record
measurements only with agreement. Before collection, document fields, worksheet
access, redaction, retention, withdrawal and deletion. No automatic upload is
permitted.

## 9. Governance and assurance alignment

These are practice references, not certifications:

- **NIST SP 800-218 SSDF 1.1** recommends integrating secure-development
  practices into the software lifecycle. SkillWatch maps to this through
  reproducible tests, code review, dependency-floor checks, release-claim
  checks, provenance records and negative controls.
- **NIST AI RMF 1.0** provides risk-management concepts for AI systems. It is
  relevant when SkillWatch is used around AI-agent assets, but SkillWatch itself
  does not use an ML model. Do not claim AI-RMF conformity.
- **OWASP SAMM** is a maturity model for improving software assurance processes.
  The repository’s ledger, review gates and pilot evidence can be assessed
  against SAMM practices, but no SAMM score has been independently assessed.
- **ISO/IEC 27001:2022** specifies requirements for an information-security
  management system. SkillWatch may support an organisation’s evidence process,
  but the project is not ISO/IEC 27001 certified.

Plain-language definitions:

- **SSDF:** a checklist of safer software-development practices.
- **AI RMF:** a way to identify, measure and manage AI-related risks.
- **SAMM:** a maturity ladder for improving software security processes.
- **ISO/IEC 27001:** a formal management-system standard for information
  security; certification requires an external conformity process.
- **SARIF:** a standard JSON format for security-tool findings.
- **SBOM:** a list of software components and versions; SkillWatch does not
  currently claim to be an SBOM generator.
- **SSRF:** a server-side request forgery attack; here, the relevant control is
  preventing requests to private or local addresses.
- **Wilson bound:** a conservative statistical interval; for a lower-is-better
  error rate, the upper end is the safety check.
- **Telemetry:** automatic collection of usage or diagnostic data.
- **Provenance:** evidence of where an observation came from and when it was
  recorded.
- **Baseline:** the first saved observation used for later comparison.

## 10. Team and responsibilities

| Responsibility | Owner now | Required evidence |
|---|---|---|
| Product/security decisions | Maintainer | Ledger entry and reviewed diff |
| Release engineering | Maintainer/CI | Green assurance gates and artefact hash |
| Participant operations | Pilot owner | Checklist and observation record |
| Privacy/data handling | Maintainer with qualified advice where needed | Consent, retention and deletion record |
| Commercial decision | Maintainer plus participant evidence | Before/after decisions and follow-through |
| Legal/licensing | Qualified legal adviser when needed | Written advice for trademarks, dual licensing or proprietary extensions |

## 11. Decision dashboard

Current decision: **run the pilot; do not claim commercial readiness**.

Pause or pivot if:

- qualified participants do not install;
- setup requires repeated maintainer operation;
- no meaningful events occur by the defined cap;
- participants do not return;
- generic monitoring satisfies the job;
- provenance does not change decisions;
- review burden exceeds perceived value;
- no participant requests an integration with a named workflow owner; or
- no commercial follow-through occurs.

Continue standalone only if the canonical pilot thresholds are met. Do not
change thresholds after seeing results without recording a new decision unit.

## 12. References and claim boundary

Primary practice references retrieved 2026-08-01:

- NIST SP 800-218, Secure Software Development Framework 1.1:
  <https://csrc.nist.gov/pubs/sp/800/218/final> (published February 2022).
- NIST AI Risk Management Framework:
  <https://www.nist.gov/itl/ai-risk-management-framework> (official framework;
  use current revision when adopting it).
- OWASP SAMM:
  <https://owasp.org/www-project-samm/> (open software-assurance maturity model).
- ISO/IEC 27001:2022:
  <https://www.iso.org/standard/27001.html> (requirements standard; certification
  is not inferred).

These sources support process recommendations only. They do not establish
SkillWatch demand, superiority, certification, safety, effectiveness or a moat.

The repository’s own evidence remains authoritative for current SkillWatch
readiness: [SHIP-READINESS.md](../SHIP-READINESS.md),
[readiness-status.json](readiness-status.json), and [OPEN-ITEMS.md](../OPEN-ITEMS.md).

