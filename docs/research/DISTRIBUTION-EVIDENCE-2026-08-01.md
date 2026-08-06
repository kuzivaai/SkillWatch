# Distribution evidence — 2026-08-01

## Question and classification

What distribution and commercial route should SkillWatch test next? This is a
bounded review, not evidence of demand. **Demonstrated** means directly reproduced
or supported by retrieved evidence; **Unverified** means asserted, inferred or
blocked; **Contradicted** means evidence conflicts with the claim.

## Search protocol

- Retrieval date: 2026-08-01.
- Indexes/surfaces: ACM Digital Library, IEEE Xplore/IEEE Access, ScienceDirect,
  SpringerLink/Empirical Software Engineering, USENIX, institutional repositories,
  official project documentation and GitHub repositories.
- Query families: `open source adoption systematic review`; `enterprise OSS
  trust support security`; `OSS newcomer barriers documentation onboarding`;
  `OSS health intake sustainability`; `commercial open source business model
  assurance adaptation assistance`; `security alert false positive habituation
  analyst burden`; `agent skill drift contract`; and exact competitor names.
- Inclusion: English peer-reviewed empirical/synthesis work whose methods or
  results inform adoption, trust, onboarding, health, commercial complements or
  review burden; official current documentation for product capabilities.
- Exclusion: vendor surveys as academic evidence, opinion/news, sources without
  inspectable methods for methodological claims, and exact price/channel claims
  unsupported by observations.
- Deduplication: DOI, then normalized title. This was bounded, not a PRISMA review;
  there is no claim of exhaustive recall or a global search-result denominator.

## Peer-reviewed source matrix

| Source | Access | Narrow supported finding | Limitation | Decision changed |
|---|---|---|---|---|
| Hauge, Ayala & Conradi, “Adoption of Open Source Software in Software-Intensive Organizations—A Systematic Literature Review,” *Information and Software Technology* 52(11), 2010, DOI [10.1016/j.infsof.2010.05.008](https://doi.org/10.1016/j.infsof.2010.05.008). | Full PDF; peer reviewed. 24,289 candidates, 112 empirical studies inspected by the review. | OSS adoption has multiple organizational modes; it is not one funnel. | Evidence through 2008; broad OSS rather than agent security. | Name the integration context and observe adoption there. |
| Rea Sanchez et al., “Open Source Adoption Factors—A Systematic Literature Review,” *IEEE Access* 8, 2020, DOI [10.1109/ACCESS.2020.2993248](https://doi.org/10.1109/ACCESS.2020.2993248). | Partial reading; peer reviewed. | Review reports technical, organizational and economic factor groups. | Heterogeneous contexts; no channel prescription. | Pilot records all three, not only CLI success. |
| Roumani, Nwankpa & Roumani, “Adopters’ Trust in Enterprise Open Source Vendors,” *JSS* 125, 2017, DOI [10.1016/j.jss.2016.12.006](https://doi.org/10.1016/j.jss.2016.12.006). | Abstract/selected sections; peer reviewed. | In a 192-person enterprise survey, security, open standards and support services associate with trust. | Association, not causal purchase evidence. | Test assurance/support as a commercial complement. |
| Steinmacher et al., “Barriers Faced by Newcomers to OSS Projects,” *IST* 59, 2015, DOI [10.1016/j.infsof.2014.11.001](https://doi.org/10.1016/j.infsof.2014.11.001). | Partial substantial text; peer reviewed. | Documentation, finding a starting point, technical hurdles and social interaction recur among newcomer barriers. | Contributor onboarding differs from product installation. | Measure maintainer intervention and unanswered questions. |
| Li et al., “Systematic Literature Review of Commercial Participation in OSS,” *ACM TOSEM* 34(2), 2025, DOI [10.1145/3690632](https://doi.org/10.1145/3690632). | Abstract/method summary; peer reviewed. | Commercial participation has economic, technical and social motives and multiple contribution models. | Does not establish microvendor revenue conversion. | Community participation is a sustained channel, not a launch event. |
| Jullien, Viseur & Zimmermann, “A Theory of FLOSS Projects and Open Source Business Models Dynamics,” *JSS* 224, 2025, DOI [10.1016/j.jss.2025.112383](https://doi.org/10.1016/j.jss.2025.112383). | Abstract/selected text; peer reviewed; full method blocked. | Commercial offers can complement FLOSS through assurance, adaptation and assistance. | Theory does not show anyone will pay SkillWatch. | Keep services as a complement subject to paid follow-through. |
| Linåker et al., “Assessing OSS Health in Organizations’ Intake Processes,” *EMSE*, 2026, DOI [10.1007/s10664-026-10846-y](https://doi.org/10.1007/s10664-026-10846-y). | Full HTML; peer reviewed. | 17 expert interviews and an automotive case show exhaustive intake assessment creates cost/friction; assessment should be contextual and risk based. | One case organization; criteria vary. | Prefer a narrow approval-workflow integration over a dashboard. |
| de Silva et al., “Trust in the Software Ecosystem,” *EMSE* 28, 2023, DOI [10.1007/s10664-022-10238-y](https://doi.org/10.1007/s10664-022-10238-y). | Full relevant HTML; peer reviewed. | Trust is multifactor; documentation is a first impression and versioned evidence matters. | Broad component-selection synthesis. | Treat stars/downloads as signals; make evidence portable/current. |
| Bravo-Lillo et al., “Harder to Ignore?”, SOUPS 2014, [USENIX](https://www.usenix.org/system/files/soups14-paper-bravo-lillo.pdf). | Full PDF; peer-reviewed conference. | Habituation reduced attention; interaction-forcing warnings resist it at usability cost. | Artificial pop-up task. | Measure repeated review and require deliberate action only when warranted. |
| Alahmadi et al., “Alert Fatigue in SOCs,” *ACM Computing Surveys*, 2025, DOI [10.1145/3723158](https://doi.org/10.1145/3723158). | Abstract/summary only; peer reviewed. | Alert volume and false positives contribute to analyst burden. | SOC work differs; review method unavailable. | Measure actionability, benign burden, review time and missed-change risk. |

## Official Codex operating evidence

The current official Codex manual was retrieved with OpenAI's helper on
2026-08-01. It recommends prompts that state goal, context, constraints and done
criteria; concise durable repository guidance in `AGENTS.md`; narrow approvals and
sandboxing; tests/gates/diff review; and bounded subagents for separable work.
This sprint therefore treats Claude-specific nouns as stale and uses Codex's
repository rules, restricted subagents and committed evidence log. Source:
[OpenAI Codex best practices](https://learn.chatgpt.com/guides/best-practices.md)
and [AGENTS.md guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md.md).

## Findings and limits

Demonstrated: literature supports context-specific OSS adoption, low-friction
intake, credible support, and alert-burden measurement. It does not establish a
SkillWatch channel, price, conversion rate or demand. The reasoned implication is
to test a narrow integration/provenance route with assurance/adaptation/assistance
as a possible commercial complement. The observation that would overturn it is
repeated independent use with explicit preference for a standalone local CLI.

Sparse or blocked: peer-reviewed agent-skill drift evidence; sponsorship versus
enterprise sales for small security CLIs; exact channel mix, timing and price;
whether this evidence changes a real approval decision. Settle these through the
pilot, an actual procurement step, and full-text retrieval of the two partial
commercial/alert papers—not by further inference.
