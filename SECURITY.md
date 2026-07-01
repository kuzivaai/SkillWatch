# Security Policy

## What SkillWatch does

SkillWatch fetches arbitrary URLs to monitor content changes. It includes SSRF protection, DNS pinning, escape sequence stripping, and per-hop redirect validation. All data is stored locally in SQLite. Nothing is sent externally.

## Reporting a vulnerability

If you find a security issue in SkillWatch, please report it by opening a GitHub issue. This is a personal open-source project, not infrastructure software, so public disclosure is appropriate.

For issues involving the SSRF protection, DNS pinning, or escape sequence stripping specifically, please email mkuziva@gmail.com first so the fix can be prepared before disclosure.

## Supported versions

Only the latest release is supported with security fixes.

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| < 0.2   | No        |
