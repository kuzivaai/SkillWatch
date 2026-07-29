"""Measure the base rate of concealment techniques on real pages.

Why this exists
---------------
`docs/HIDING-TECHNIQUE-TAXONOMY.md` originally assigned every hiding technique to
a bucket on one criterion: *does this conceal content from a human reader?* That
criterion cannot distinguish a detection from a false-positive generator. A
technique that conceals content **and** appears on most ordinary pages is the
latter. This script supplies the missing input: how often each technique occurs on
pages this project did not write.

What the corpus is
------------------
`analysis/corpus/realpage/MANIFEST.json` — every page referenced by a real
`SKILL.md` sampled from public GitHub repositories, fetched with SkillWatch's own
`fetch_url`. None of these pages is known or assumed to carry a payload, so every
occurrence counted here is a legitimate use. That is what makes it a base rate.

Two figures, and why they differ by two orders of magnitude
-----------------------------------------------------------
`hidden_content` and the other HTML checks are **delta** checks: they flag content
that is newly hidden, not content that is hidden. Two consequences the reader must
not conflate:

* **Technique prevalence** ("what fraction of real pages carry this at all") is
  measured exactly from a single snapshot. It is the input the taxonomy needs.
* **False-positive rate** is *not* prevalence. `cli.py` establishes a baseline on
  first fetch without running detection at all, and runs detection only when the
  extracted text hash changes. So a page that permanently contains a collapsed
  accordion never produces an alert.

The first-observation column below is therefore reported as *exposure*, not as a
false-positive rate, and is labelled as such wherever it appears.
"""

import importlib.util
import json
import sys

from pathlib import Path
from types import ModuleType

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "corpus" / "realpage" / "MANIFEST.json"


def _load_sibling(name: str) -> ModuleType:
    """Load a sibling module in `analysis/` by path.

    `analysis/` is not a package, so `import measure_efficacy` would need a
    sys.path insert followed by a module-level import — the E402 pattern that can
    only be silenced with a lint suppression. This is the same importlib loader
    `tests/test_dependency_floors.py` already uses, so none is required.
    """
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    if spec is None or spec.loader is None:
        raise SystemExit(f"FAIL: cannot load analysis/{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_efficacy = _load_sibling("measure_efficacy")
fmt_prop = _efficacy.fmt_prop
wilson_interval = _efficacy.wilson_interval

# Techniques the taxonomy names, in the order the document lists them. Keys match
# the technique identifiers in `skillwatch.detector.TECHNIQUE_BUCKETS`.
_REPORT_ORDER = (
    "display:none",
    "visibility:hidden",
    "opacity:0",
    "font-size:0",
    "zero-box-clipped",
    "offscreen-position",
    "html-hidden-attr",
    "clip-path-inset",
    "text-indent-negative",
    "aria-hidden",
)


def load_manifest() -> dict:
    """Read the tracked manifest, or exit with a clear message if it is absent."""
    if not MANIFEST.exists():
        print(f"FAIL: no manifest at {MANIFEST}", file=sys.stderr)
        print("This check has NOT passed — it could not inspect its subject.", file=sys.stderr)
        raise SystemExit(2)
    with MANIFEST.open() as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SystemExit("FAIL: manifest is not an object")
    return data


def main() -> int:
    data = load_manifest()
    items = data["items"]
    n = len(items)

    print("=" * 66)
    print("REAL-PAGE BASE RATE — concealment techniques on pages we did not write")
    print("=" * 66)
    print(f"\nCorpus: {n} pages, referenced by {data['method']['skill_files_sampled']} real "
          f"SKILL.md files\n        across {data['method']['distinct_repositories']} "
          f"distinct repositories.")
    print("Every occurrence below is a LEGITIMATE use — no page here carries a payload.\n")

    pages_with: dict[str, int] = {}
    occurrences: dict[str, int] = {}
    for item in items:
        for technique, count in item["techniques"].items():
            if "(" in technique:  # the inline/style-block split, reported separately
                continue
            pages_with[technique] = pages_with.get(technique, 0) + 1
            occurrences[technique] = occurrences.get(technique, 0) + count

    print(f"{'technique':<24} {'pages carrying it':<34} {'occurrences':>11}")
    print("-" * 72)
    for technique in _REPORT_ORDER:
        k = pages_with.get(technique, 0)
        print(f"{technique:<24} {fmt_prop(k, n):<34} {occurrences.get(technique, 0):>11}")

    # First observation: what WOULD fire if a whole page were treated as new.
    # This is exposure, not a false-positive rate — see the module docstring.
    exposure: dict[str, int] = {}
    for item in items:
        for code in item["flags_first_observation"]:
            exposure[code] = exposure.get(code, 0) + 1

    print(f"\n{'-' * 72}")
    print("EXPOSURE (not a false-positive rate): flags that would fire if a whole")
    print("page were treated as newly added. `cli.py` never does this — a first")
    print("fetch is a baseline that runs no detection. Reported to size the risk.")
    print("-" * 72)
    for code in sorted(exposure, key=lambda c: -exposure[c]):
        print(f"  {code:<24} {fmt_prop(exposure[code], n)}")

    # The deployment-faithful figure: detection runs only when the extracted text
    # hash changes between two scans.
    paired = [i for i in items if "snapshot_2" in i]
    text_changed = [i for i in paired if i["snapshot_2"]["extracted_text_changed"]]
    html_changed = [i for i in paired if i["snapshot_2"]["raw_html_changed"]]
    flagged = [i for i in text_changed if i.get("flags_on_delta")]

    print(f"\n{'-' * 72}")
    print("DELTA — the figure that transfers, and why it is not yet informative")
    print("-" * 72)
    print(f"  paired snapshots           {len(paired)}")
    print(f"  raw HTML changed           {fmt_prop(len(html_changed), len(paired))}")
    print(f"  extracted text changed     {fmt_prop(len(text_changed), len(paired))}")
    print("    ^ this is the gate: cli.py runs detection only on a text diff.")
    print(f"\n  false positives            {fmt_prop(len(flagged), len(text_changed))}")

    delta_flags: dict[str, int] = {}
    for item in text_changed:
        for code in item.get("flags_on_delta", []):
            delta_flags[code] = delta_flags.get(code, 0) + 1
    for code in sorted(delta_flags, key=lambda c: -delta_flags[c]):
        print(f"    {code:<22} {fmt_prop(delta_flags[code], len(text_changed))}")
    if not delta_flags:
        print("    (no flag fired on any text-diffing page)")

    lo, hi = wilson_interval(len(flagged), len(text_changed))
    print(f"\n  n={len(text_changed)} is too small to support any claim: the interval is")
    print(f"  [{lo:.1%}, {hi:.1%}], which is consistent with almost any true rate.")
    print("  The snapshots are minutes apart; editorial drift needs days. This")
    print("  figure is PENDING a second pass at a realistic interval.")

    print(f"\n{'-' * 72}")
    print("LIMITATIONS (also recorded in the manifest)")
    print("-" * 72)
    for limitation in data["limitations"]:
        print(f"  - {limitation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
