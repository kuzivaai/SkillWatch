"""Build SARIF 2.1.0 output from scan results.

SARIF is the format GitHub Code Scanning ingests, so `skillwatch scan --output
sarif` can be uploaded from CI alongside static scanners (Cisco skill-scanner,
SkillTotal, etc.) that also emit SARIF. No detection logic lives here; this only
reshapes alerts SkillWatch already produced.
"""

from . import __version__
from .detector import explain

_SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"
_INFO_URI = "https://github.com/kuzivaai/SkillWatch"
_HELP_URI = f"{_INFO_URI}/blob/main/docs/UNDERSTANDING-ALERTS.md"

# SkillWatch severity -> SARIF result level.
_LEVEL = {"critical": "error", "warning": "warning", "info": "note"}


def build_sarif(changed_results: list[dict]) -> dict:
    """Build a SARIF 2.1.0 document from the "changed" entries of a scan.

    Each entry is `{"url": str, "severity": str, "flags": [{"code", "severity",
    ...}]}` (the same shape the JSON output already builds). One SARIF result is
    emitted per flag so each finding is a separate, rule-tagged entry, with the
    monitored URL as its location.
    """
    rules: dict[str, dict] = {}
    results: list[dict] = []

    for entry in changed_results:
        url = entry.get("url", "")
        for flag in entry.get("flags", []):
            code = flag.get("code", "")
            if code and code not in rules:
                rules[code] = {
                    "id": code,
                    "name": code,
                    "shortDescription": {"text": explain(code)},
                    "helpUri": _HELP_URI,
                }
            results.append({
                "ruleId": code,
                "level": _LEVEL.get(flag.get("severity", "info"), "note"),
                "message": {"text": f"{explain(code)} ({code})"},
                "locations": [
                    {"physicalLocation": {"artifactLocation": {"uri": url}}}
                ],
            })

    return {
        "$schema": _SARIF_SCHEMA,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "SkillWatch",
                        "version": __version__,
                        "informationUri": _INFO_URI,
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }
