# Unicode Confusables Data Provenance

## Current state

SkillWatch uses the `confusable_homoglyphs` library (v3.3.1, MIT licence)
for Unicode homoglyph detection. The library ships with pre-built JSON data
derived from the Unicode Consortium's confusables database.

## Data source

- **Source file:** `confusables.txt` from the Unicode Security Mechanisms (UTS #39)
- **URL:** https://www.unicode.org/Public/security/latest/confusables.txt
- **Licence:** Unicode Character Database Terms of Use (https://www.unicode.org/copyright.html)
- **Freely redistributable:** Yes

## Library version and data currency

- **Library version:** 3.3.1 (last PyPI release: 2019-01-06)
- **Approximate Unicode version of shipped data:** 11.0 (2018)
- **Current Unicode version:** 16.0 (September 2024)
- **Entries in shipped data:** 9,619 confusable character mappings

## Coverage assessment

The shipped data covers all major homoglyph attack scripts used in practice:

| Script | Covered | Risk level |
|--------|---------|------------|
| Cyrillic (а→a, о→o, etc.) | Yes | High — most common attack vector |
| Greek (ο→o, Α→A, etc.) | Yes | High |
| Cherokee (Ꭰ→D, etc.) | Yes | Medium |
| Armenian | Yes | Medium |
| Georgian | Yes | Low |
| Osage (Unicode 10.0) | Yes | Low |
| Ahom (Unicode 8.0) | Yes | Low |
| Lisu (Unicode 5.2) | Yes | Low |
| Tangsa (Unicode 14.0) | No | Very low — extremely niche script |
| Cypro-Minoan (Unicode 15.0) | No | Very low — archaeological script |

## Gap assessment

Scripts added in Unicode 12.0+ that are missing from the shipped data are
exclusively niche or archaeological scripts (Tangsa, Cypro-Minoan, Vithkuqi,
etc.). These are not realistic homoglyph attack vectors because:

1. They have no visual similarity to Latin characters in standard fonts
2. Most systems do not render them at all (tofu/fallback glyphs)
3. No documented homoglyph attacks use these scripts

The practical detection gap from stale data is **negligible** for
SkillWatch's use case.

## Refresh procedure

To update the confusables data to the latest Unicode version:

```bash
pip install 'confusable_homoglyphs[cli]'
python scripts/refresh_confusables.py
```

Or manually:
```bash
python -c "from confusable_homoglyphs.cli import update; update()"
```

This downloads fresh data from unicode.org and overwrites the library's
shipped JSON files. The refresh is safe — the library's API is unchanged.

## Maintained alternatives

As of July 2026, there is no maintained drop-in alternative to
`confusable_homoglyphs`. The library itself works correctly on Python 3.12
despite not having received updates since 2019. The only gap is data
currency, not functionality.

---

# freeTSA CA Certificate Provenance

## Purpose

`freetsa_cacert.pem` is bundled so that RFC 3161 timestamp tokens obtained by
`skillwatch anchor` from the default authority (freeTSA.org) can be verified
**offline** — `skillwatch verify` checks the token's signature against this root.

## Source

- **File:** `skillwatch/data/freetsa_cacert.pem`
- **Source URL:** https://freetsa.org/files/cacert.pem
- **Subject:** `CN=www.freetsa.org, OU=Root CA, O=Free TSA` (self-signed root)
- **Validity:** 2016-03-13 to **2041-03-07** (UTC)
- **Freely redistributable:** Yes — freeTSA publishes it for public verification.

## Notes

- This root only verifies tokens from freeTSA.org. Anchoring against a different
  RFC 3161 authority (`skillwatch anchor --tsa <url>`) requires that authority's
  CA certificate to verify; freeTSA is the default because its tokens parse
  cleanly with `rfc3161-client` (DigiCert's, for example, do not).
- To refresh: re-download from the source URL above and replace the file. The
  bundled copy captured 2026-07-11.
