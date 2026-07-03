# G-04: Source Independence Verification

**Date:** 2026-07-03
**Assessor:** Claude Code (Opus 4.6)
**Question:** Are the CSA and arxiv sources cited in DECISION.md independent of AIR?

## Background

DECISION.md condition 4 requires "minimum one independent, non-conflicted
evidence source for the problem premise." The two corroborating sources are:

1. **CSA research note** (May 2026): "Agent Context Poisoning: SKILL.md and
   the New AI Supply Chain Attack Surface"
2. **arxiv 2508.12538** (August 2025, revised May 2026): "MCPXKIT: The
   Unified Toolkit for Analyzing Model Context Protocol Security"

AIR (air.security) is the party with the conflict of interest -- they
published "The Story of Skills" while simultaneously launching a managed
skill marketplace (skills.sh).

## Findings

### arxiv 2508.12538

- **Authors:** Yongjian Guo, Puzhuo Liu, Wanlun Ma, Zehang Deng, Xiaogang
  Zhu, Peng Di, Xi Xiao, Sheng Wen
- **Affiliations identified:** Tsinghua University (Shenzhen), Chinese
  Academy of Sciences, Swinburne University of Technology
- **AIR connection:** No affiliation with AIR or air.security found.
  All identified affiliations are academic institutions.
- **Assessment:** LIKELY INDEPENDENT. Academic paper from multiple
  universities with no commercial AI agent security product. However,
  full affiliation verification was done via web search, not by reading
  the PDF title page directly.

### CSA research note

- **Author attribution:** "Cloud Security Alliance AI Safety Initiative"
  (no individual authors named)
- **AIR connection:** The note cites external research from Snyk, Check
  Point Research, and Embrace the Red. AIR is not listed as a contributor
  or cited source in the web version of the note.
- **Assessment:** LIKELY INDEPENDENT. CSA is an industry body with its
  own research programme. The note does not cite AIR's "Story of Skills"
  blog post. However, CSA membership includes many security vendors, and
  individual contributor affiliations are not disclosed.

## Verdict

**LIKELY INDEPENDENT, but not VERIFIED.**

Both sources appear independent of AIR based on available evidence:
- The arxiv authors are at academic institutions (Tsinghua, CAS, Swinburne)
- The CSA note is attributed to CSA's own research initiative, not AIR

What I checked:
- arxiv paper author names and affiliations (via arxiv.org HTML version)
- CSA research note author attribution (via CSA Labs website)
- Web searches for author-AIR connections (none found)

What I could not check:
- Whether any individual CSA AI Safety Initiative contributor works at AIR
- Whether any arxiv author has undisclosed consulting relationships with AIR
- The full PDF title page of the arxiv paper (WebFetch did not render
  the affiliation legend)

**Recommendation:** Record as LIKELY INDEPENDENT. Do NOT weaken the COI
disclosure in README.md -- the disclosure is about AIR's blog post, not
about these corroborating sources. The existence of independent
corroboration strengthens the premise but does not eliminate the need to
disclose AIR's commercial interest.
