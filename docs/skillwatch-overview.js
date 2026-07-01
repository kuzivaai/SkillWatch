const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel,
  BorderStyle, WidthType, ShadingType, VerticalAlign, PageNumber, PageBreak
} = require("docx");

const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "BBBBBB" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };
const headerShading = { fill: "1B3A5C", type: ShadingType.CLEAR };
const altRowShading = { fill: "F2F6FA", type: ShadingType.CLEAR };

function headerCell(text, width) {
  return new TableCell({
    borders: cellBorders, width: { size: width, type: WidthType.DXA },
    shading: headerShading, verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 60 },
      children: [new TextRun({ text, bold: true, size: 20, font: "Calibri", color: "FFFFFF" })] })]
  });
}

function cell(text, width, opts = {}) {
  return new TableCell({
    borders: cellBorders, width: { size: width, type: WidthType.DXA },
    shading: opts.shaded ? altRowShading : undefined,
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({ spacing: { before: 40, after: 40 },
      children: [new TextRun({ text, size: 19, font: "Calibri", bold: opts.bold || false })] })]
  });
}

function bulletCell(items, width, opts = {}) {
  return new TableCell({
    borders: cellBorders, width: { size: width, type: WidthType.DXA },
    shading: opts.shaded ? altRowShading : undefined,
    verticalAlign: VerticalAlign.TOP,
    children: items.map(t => new Paragraph({ spacing: { before: 20, after: 20 },
      children: [new TextRun({ text: "\u2022 " + t, size: 18, font: "Calibri" })] }))
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 48, bold: true, color: "1B3A5C", font: "Calibri" },
        paragraph: { spacing: { before: 0, after: 80 }, alignment: AlignmentType.LEFT } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: "1B3A5C", font: "Calibri" },
        paragraph: { spacing: { before: 240, after: 100 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: "2D5F8A", font: "Calibri" },
        paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 1 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    ]
  },
  sections: [{
    properties: {
      page: { margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 },
        pageNumbers: { start: 1 } }
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "SkillWatch v0.2.0  |  July 2026  |  Confidential", size: 16, color: "999999", font: "Calibri", italics: true })]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Page ", size: 16, color: "999999", font: "Calibri" }),
          new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "999999", font: "Calibri" }),
          new TextRun({ text: " of ", size: 16, color: "999999", font: "Calibri" }),
          new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, color: "999999", font: "Calibri" })]
      })] })
    },
    children: [
      // === PAGE 1 ===
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("SkillWatch")] }),
      new Paragraph({ spacing: { after: 200 },
        children: [new TextRun({ text: "Continuous URL Content Monitoring for AI Agent Skills", size: 24, color: "555555", italics: true, font: "Calibri" })] }),

      new Paragraph({ spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: "1B3A5C" } },
        children: [new TextRun({ text: "July 2026  |  v0.2.0  |  Apache 2.0  |  Python 3.10+", size: 18, color: "888888", font: "Calibri" })] }),

      // What It Is
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("What It Is")] }),
      new Paragraph({ spacing: { after: 120 },
        children: [new TextRun({ text: "SkillWatch is a free, open-source command-line tool that monitors the web pages referenced by AI agent skills and plugins. It runs on your laptop, costs nothing, and stores everything locally in SQLite.", size: 21, font: "Calibri" })] }),
      new Paragraph({ spacing: { after: 160 },
        children: [new TextRun({ text: "When an AI coding assistant installs a skill from a marketplace, that skill often points the assistant to external URLs for setup instructions or documentation. SkillWatch watches those URLs and alerts you when their content changes, particularly when the changes look suspicious. It detects 13 distinct threat patterns including prompt injection in 7 languages (32 ATR-derived patterns), Unicode homoglyph attacks (backed by the Unicode Consortium's confusables database), data URI payloads, credential harvesting keywords, and suspicious HTML injection.", size: 21, font: "Calibri" })] }),

      // Why It Matters
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Why It Matters")] }),
      new Paragraph({ spacing: { after: 120 },
        children: [new TextRun({ text: "In June 2026, security researchers at AIR demonstrated that a fake AI skill could bypass every major security scanner (Cisco, NVIDIA, skills.sh) by keeping its own code clean while pointing to an external URL. After distribution, the URL content was swapped from legitimate documentation to malicious instructions. The ClawHavoc campaign reportedly compromised over 1,184 skills using similar supply chain techniques (source: Orca Security, unverified against primary disclosure).", size: 21, font: "Calibri" })] }),
      new Paragraph({ spacing: { after: 120 },
        children: [new TextRun({ text: "Every existing scanner checks skills once, at install time. None re-checks what happens at those URLs afterwards. SkillWatch fills this specific gap. It is designed as a complement to tools like Snyk Agent Scan, not a replacement.", size: 21, font: "Calibri" })] }),

      // Key Metrics
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Key Metrics")] }),
      new Table({
        columnWidths: [3600, 3600],
        rows: [
          new TableRow({ children: [headerCell("Metric", 3600), headerCell("Value", 3600)] }),
          new TableRow({ children: [cell("Source code", 3600), cell("1,733 lines across 8 modules", 3600)] }),
          new TableRow({ children: [cell("Test coverage", 3600, { shaded: true }), cell("200 tests, 95% line coverage", 3600, { shaded: true })] }),
          new TableRow({ children: [cell("Detection patterns", 3600), cell("13 flag codes, 32 prompt injection patterns (ATR-derived)", 3600)] }),
          new TableRow({ children: [cell("Languages covered", 3600, { shaded: true }), cell("EN, DE, ES, FR, AR, RU, SR/HR + 6 obfuscation types", 3600, { shaded: true })] }),
          new TableRow({ children: [cell("Dependencies", 3600), cell("5 direct, all Apache/MIT/BSD licensed", 3600)] }),
          new TableRow({ children: [cell("Infrastructure cost", 3600, { shaded: true }), cell("Zero (runs on developer laptop via cron)", 3600, { shaded: true })] }),
          new TableRow({ children: [cell("Output formats", 3600), cell("Text (human) and JSON (machine-readable)", 3600)] }),
          new TableRow({ children: [cell("CI/CD", 3600, { shaded: true }), cell("GitHub Actions (Python 3.10-3.13) + GitHub Action for users", 3600, { shaded: true })] }),
          new TableRow({ children: [cell("Licence", 3600), cell("Apache 2.0 (free for commercial use)", 3600)] }),
        ]
      }),

      // Market Opportunity
      new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 240 }, children: [new TextRun("Market Opportunity")] }),
      new Paragraph({ spacing: { after: 120 },
        children: [new TextRun({ text: "The AI agent ecosystem is growing rapidly. ClawHub hosts 3,286 skills, the Claude Code marketplace has 101 plugins, and over 9,652 MCP servers are registered. However, the subset of developers who install untrusted third-party skills AND are aware of supply chain risks is likely in the low thousands at most. No published data quantifies this segment.", size: 21, font: "Calibri" })] }),
      new Paragraph({ spacing: { after: 120 },
        children: [
          new TextRun({ text: "Direct revenue: zero.", size: 21, font: "Calibri", bold: true }),
          new TextRun({ text: " Every comparable tool is free. The market prices individual developer security tools at zero. SkillWatch is free and open source by design. Its value is indirect: as a credibility asset for AI governance consulting and a portfolio piece that demonstrates practical security expertise.", size: 21, font: "Calibri" }),
        ] }),

      // === PAGE 2 ===
      new Paragraph({ children: [new PageBreak()] }),

      // SWOT Analysis
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SWOT Analysis")] }),
      new Paragraph({ spacing: { after: 60 },
        children: [new TextRun({ text: "Updated 1 July 2026 to reflect current state after development. Supersedes the June 2026 version.", size: 18, font: "Calibri", italics: true, color: "666666" })] }),
      new Table({
        columnWidths: [4680, 4680],
        rows: [
          new TableRow({ children: [headerCell("Strengths", 4680), headerCell("Weaknesses", 4680)] }),
          new TableRow({ children: [
            bulletCell([
              "Only free tool monitoring URL content changes for AI skills",
              "13 detection patterns, 32 prompt injection patterns covering 7 languages",
              "ATR-derived patterns (same rules used by Microsoft AGT and Cisco AI Defense)",
              "Unicode homoglyph detection via Unicode Consortium official database",
              "JSON output for CI/CD integration, webhooks, and notification piping",
              "Built-in false positive preset (timestamps, UUIDs, build hashes)",
              "Comprehensive SSRF protection with DNS pinning",
              "Zero infrastructure cost, fully offline, nothing sent externally",
              "200 tests, 95% coverage, GitHub Actions CI on Python 3.10-3.13",
            ], 4680),
            bulletCell([
              "Zero community adoption (not yet published)",
              "CLI only, no web UI or browser extension",
              "Regex-based detection, no semantic/LLM analysis (by design, avoids 2.5GB dep)",
              "Does not scan skill code or metadata directly (by design, other tools do this)",
              "No enterprise features (by design, not the target market)",
              "Evasion via IP-based cloaking or JS rendering (documented limitation)",
              "ClawHavoc 1,184 figure unverified against primary source",
            ], 4680),
          ] }),
          new TableRow({ children: [headerCell("Opportunities", 4680), headerCell("Threats", 4680)] }),
          new TableRow({ children: [
            bulletCell([
              "MCP ecosystem growing rapidly (9,652+ servers)",
              "TIL newsletter article drives awareness (not yet written)",
              "AI governance consulting credibility asset",
              "PyPI publishing ready (name available, workflows built, not yet published)",
              "GitHub Action built for CI/CD pipeline users",
              "Landing page with SEO/GEO optimisation (Schema.org + FAQ structured data)",
              "No competitor covers this specific gap yet (verified June 2026)",
            ], 4680),
            bulletCell([
              "Snyk could add URL monitoring in 3-6 months",
              "Anthropic could add platform-level URL verification",
              "AI skill adoption may not reach critical mass",
              "False positive rate could erode user trust (mitigated by presets)",
              "changedetection.io (32K stars) could add skill awareness",
              "Window for first mover is ~6-12 months, clock started June 2026",
              "Tool is built but not deployed. Every day undeployed is a day lost.",
            ], 4680),
          ] }),
        ]
      }),

      // TAM, SAM, SOM
      new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 240 }, children: [new TextRun("TAM, SAM, SOM")] }),
      new Paragraph({ spacing: { after: 60 },
        children: [new TextRun({ text: "Note: These figures are estimates. No published data quantifies the addressable market for AI skill security monitoring at the individual developer level. All numbers should be treated as unverified.", size: 19, font: "Calibri", italics: true, color: "666666" })] }),
      new Table({
        columnWidths: [1800, 2520, 5040],
        rows: [
          new TableRow({ children: [headerCell("Segment", 1800), headerCell("Estimate", 2520), headerCell("Basis", 5040)] }),
          new TableRow({ children: [
            cell("TAM", 1800, { bold: true }),
            cell("~50,000-100,000", 2520),
            cell("Developers who install third-party AI skills/MCP tools globally. Derived from 9,652 registered MCP servers, 3,286 ClawHub skills, and estimated user bases of Claude Code, Cursor, Windsurf.", 5040),
          ] }),
          new TableRow({ children: [
            cell("SAM", 1800, { bold: true, shaded: true }),
            cell("~5,000-15,000", 2520, { shaded: true }),
            cell("Security-conscious developers who are aware of supply chain risks AND install third-party skills. Subset who already use tools like Snyk, MCP-Scan, or follow AI security discussions.", 5040, { shaded: true }),
          ] }),
          new TableRow({ children: [
            cell("SOM", 1800, { bold: true }),
            cell("30-500 users (3 months)", 2520),
            cell("Based on comparable launches: TheAuditor (547 stars/9 months), AgentArmor (90 stars), Agentsec (7 stars). HN score explains only 8% of variance in GitHub stars. Pessimistic: 30, base: 100, optimistic: 500.", 5040),
          ] }),
        ]
      }),

      // Honest Assessment
      new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 240 }, children: [new TextRun("Honest Assessment")] }),
      new Paragraph({ spacing: { after: 100 },
        children: [new TextRun({ text: "SkillWatch fills a genuine, documented gap in AI agent security. No other free tool continuously monitors external URL content referenced by skills. This gap is independently validated by the AIR experiment, the ClawHavoc campaign, and the Cloud Security Alliance's research note on SKILL.md context poisoning (May 2026).", size: 21, font: "Calibri" })] }),
      new Paragraph({ spacing: { after: 100 },
        children: [new TextRun({ text: "Detection depth has improved significantly since v0.1: prompt injection now covers 7 languages and 6 obfuscation techniques using 32 patterns derived from ATR (Agent Threat Rules), the same open standard adopted by Microsoft and Cisco. Unicode detection uses the Unicode Consortium's official confusables database. However, it remains regex-based, not semantic. LLM-based detection was evaluated and rejected: it requires PyTorch (2.5GB+), contradicting the tool's zero-infrastructure value proposition.", size: 21, font: "Calibri" })] }),
      new Paragraph({ spacing: { after: 100 },
        children: [new TextRun({ text: "The competitive window is approximately 6-12 months before Snyk or Anthropic close the gap. The tool is fully built but not yet deployed. PyPI publishing, GitHub push, and the TIL article are the critical next steps. The tool does not need to be the permanent solution. It needs to be the first, and it needs to be a credible portfolio piece.", size: 21, font: "Calibri" })] }),
      new Paragraph({ spacing: { after: 100 },
        children: [
          new TextRun({ text: "Revenue model: none from the tool.", size: 21, font: "Calibri", bold: true }),
          new TextRun({ text: " The indirect path is: free tool (credibility) + article (reach) leading to AI governance consulting positioning. This pipeline is unverified. No documented cases exist of a solo developer converting a free security tool into consulting leads. The tool strengthens an existing pitch; it does not create the conversation.", size: 21, font: "Calibri" }),
        ] }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("/mnt/c/Users/mkuzi/Downloads/SkillWatch-Overview-v3.docx", buf);
  console.log("Written to /mnt/c/Users/mkuzi/Downloads/SkillWatch-Overview-v3.docx");
});
