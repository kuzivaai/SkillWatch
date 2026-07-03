"""Measure SkillWatch detection efficacy against labelled corpus.

Imports the detector without modification. Runs every corpus item through
detect_suspicious_changes and records: true label, detector verdict, flag codes.
Computes FP/FN rates, precision, recall.
"""

import json
import os
import sys

# Add project root to path so we can import skillwatch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skillwatch.detector import detect_suspicious_changes
from skillwatch.differ import generate_diff

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "corpus")


def _make_diff(old_text: str, new_text: str) -> str:
    """Generate a unified diff between old and new text."""
    return generate_diff(old_text, new_text)


def _load_corpus(subset_dir: str) -> list[dict]:
    """Load all JSON items from a corpus subdirectory."""
    items = []
    path = os.path.join(CORPUS_DIR, subset_dir)
    if not os.path.exists(path):
        return items
    for fname in sorted(os.listdir(path)):
        if fname.endswith(".json"):
            with open(os.path.join(path, fname)) as f:
                items.append(json.load(f))
    return items


def _run_detector(item: dict) -> dict:
    """Run the detector on a corpus item and return results."""
    old_text = item["old"]
    new_text = item["new"]
    diff_text = _make_diff(old_text, new_text)

    # Pass HTML content when present (for HTML-level flag codes)
    old_html = item.get("old_html")
    new_html = item.get("new_html")

    flags = detect_suspicious_changes(
        old_text=old_text,
        new_text=new_text,
        diff_text=diff_text,
        old_html=old_html,
        new_html=new_html,
    )

    flag_codes = [f.code for f in flags]
    detected = len(flags) > 0

    return {
        "id": item["id"],
        "true_label": item["label"],
        "subset": item["subset"],
        "detected": detected,
        "flag_codes": flag_codes,
        "verdict": "flagged" if detected else "clean",
    }


def _print_corpus_report(label: str, items: list[dict]) -> dict:
    """Run the detector on a list of corpus items and print a report.

    Returns a structured results dict.
    """
    all_results = []
    for item in items:
        result = _run_detector(item)
        all_results.append(result)

    benign_results = [r for r in all_results if r["true_label"] == "benign"]
    benign_hash = [r for r in benign_results if r["subset"] == "hash"]
    benign_standard = [r for r in benign_results if r["subset"] == "standard"]
    adv_a_results = [r for r in all_results if r["subset"] == "A"]
    adv_b_results = [r for r in all_results if r["subset"] == "B"]

    fp_benign = sum(1 for r in benign_results if r["detected"])
    fp_hash = sum(1 for r in benign_hash if r["detected"])
    fp_standard = sum(1 for r in benign_standard if r["detected"])

    fn_a = sum(1 for r in adv_a_results if not r["detected"])
    fn_b = sum(1 for r in adv_b_results if not r["detected"])

    fp_rate_overall = fp_benign / len(benign_results) if benign_results else 0
    fp_rate_hash = fp_hash / len(benign_hash) if benign_hash else 0
    fp_rate_standard = fp_standard / len(benign_standard) if benign_standard else 0
    fn_rate_a = fn_a / len(adv_a_results) if adv_a_results else 0
    fn_rate_b = fn_b / len(adv_b_results) if adv_b_results else 0

    true_positives = sum(1 for r in all_results if r["true_label"] == "malicious" and r["detected"])
    false_positives = fp_benign
    false_negatives = fn_a + fn_b
    true_negatives = sum(1 for r in benign_results if not r["detected"])

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0

    evasive_detected = sum(1 for r in adv_b_results if r["detected"])
    evasive_total = len(adv_b_results)
    evasive_recall = evasive_detected / evasive_total if evasive_total > 0 else 0

    fp_by_code: dict[str, int] = {}
    for r in benign_results:
        if r["detected"]:
            for code in r["flag_codes"]:
                fp_by_code[code] = fp_by_code.get(code, 0) + 1

    print(f"\n{'='*60}")
    print(f"DETECTION EFFICACY RESULTS — {label}")
    print(f"{'='*60}")
    print(f"\nCorpus: {len(benign_results)} benign ({len(benign_hash)} hash, {len(benign_standard)} standard)")
    print(f"        {len(adv_a_results)} adversarial A (pattern-matching)")
    print(f"        {len(adv_b_results)} adversarial B (evasive)")
    print(f"\nTP: {true_positives}  FP: {false_positives}  TN: {true_negatives}  FN: {false_negatives}")
    print(f"\nFalse-positive rate (overall):  {fp_benign}/{len(benign_results)} = {fp_rate_overall:.1%}")
    if benign_hash:
        print(f"False-positive rate (hash):     {fp_hash}/{len(benign_hash)} = {fp_rate_hash:.1%}")
    if benign_standard:
        print(f"False-positive rate (standard): {fp_standard}/{len(benign_standard)} = {fp_rate_standard:.1%}")
    if adv_a_results:
        print(f"\nFalse-negative rate (subset A): {fn_a}/{len(adv_a_results)} = {fn_rate_a:.1%}")
    print(f"False-negative rate (subset B): {fn_b}/{len(adv_b_results)} = {fn_rate_b:.1%}")
    print(f"\nPrecision: {precision:.1%}")
    print(f"Recall:    {recall:.1%}")
    print(f"Evasive recall: {evasive_detected}/{evasive_total} = {evasive_recall:.1%}")

    if fp_by_code:
        print("\nFP breakdown by flag code:")
        for code, count in sorted(fp_by_code.items(), key=lambda x: -x[1]):
            print(f"  {code}: {count}/{len(benign_results)} = {count/len(benign_results):.1%}")

    print(f"\n{'='*60}")
    print("PER-ITEM RESULTS")
    print(f"{'='*60}")
    print(f"{'ID':<8} {'Label':<10} {'Subset':<10} {'Verdict':<8} {'Flag Codes'}")
    print("-" * 70)
    for r in all_results:
        codes = ", ".join(r["flag_codes"]) if r["flag_codes"] else "(none)"
        marker = ""
        if r["true_label"] == "benign" and r["detected"]:
            marker = " <-- FP"
        elif r["true_label"] == "malicious" and not r["detected"]:
            marker = " <-- FN"
        print(f"{r['id']:<8} {r['true_label']:<10} {r['subset']:<10} {r['verdict']:<8} {codes}{marker}")

    return {
        "benign_count": len(benign_results),
        "hash_count": len(benign_hash),
        "standard_count": len(benign_standard),
        "adv_a_count": len(adv_a_results),
        "adv_b_count": len(adv_b_results),
        "fp_overall": fp_benign,
        "fp_hash": fp_hash,
        "fp_standard": fp_standard,
        "fn_a": fn_a,
        "fn_b": fn_b,
        "fp_rate_overall": fp_rate_overall,
        "fp_rate_hash": fp_rate_hash,
        "fn_rate_a": fn_rate_a,
        "fn_rate_b": fn_rate_b,
        "precision": precision,
        "recall": recall,
        "evasive_recall": evasive_recall,
        "evasive_detected": evasive_detected,
        "evasive_total": evasive_total,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "true_negatives": true_negatives,
        "false_negatives": false_negatives,
        "fp_by_code": fp_by_code,
        "all_results": all_results,
    }


def _print_html_report(items: list[dict]) -> dict:
    """Run the detector on HTML corpus items and print a report.

    Returns a structured results dict.
    """
    all_results = []
    for item in items:
        result = _run_detector(item)
        all_results.append(result)

    malicious = [r for r in all_results if r["true_label"] == "malicious"]
    benign = [r for r in all_results if r["true_label"] == "benign"]

    tp = sum(1 for r in malicious if r["detected"])
    fn = sum(1 for r in malicious if not r["detected"])
    fp = sum(1 for r in benign if r["detected"])
    tn = sum(1 for r in benign if not r["detected"])

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    fp_by_code: dict[str, int] = {}
    for r in benign:
        if r["detected"]:
            for code in r["flag_codes"]:
                fp_by_code[code] = fp_by_code.get(code, 0) + 1

    print(f"\n{'='*60}")
    print("DETECTION EFFICACY RESULTS — HTML CORPUS")
    print(f"{'='*60}")
    print(f"\nCorpus: {len(malicious)} malicious, {len(benign)} benign")
    print(f"\nTP: {tp}  FP: {fp}  TN: {tn}  FN: {fn}")
    print(f"\nFP rate: {fp}/{len(benign)} = {fp/len(benign):.1%}" if benign else "")
    print(f"FN rate: {fn}/{len(malicious)} = {fn/len(malicious):.1%}" if malicious else "")
    print(f"\nPrecision: {precision:.1%}")
    print(f"Recall:    {recall:.1%}")

    if fp_by_code:
        print("\nFP breakdown by flag code:")
        for code, count in sorted(fp_by_code.items(), key=lambda x: -x[1]):
            print(f"  {code}: {count}/{len(benign)} = {count/len(benign):.1%}")

    print(f"\n{'='*60}")
    print("PER-ITEM RESULTS")
    print(f"{'='*60}")
    print(f"{'ID':<12} {'Label':<12} {'Subset':<16} {'Verdict':<8} {'Flag Codes'}")
    print("-" * 80)
    for r in all_results:
        codes = ", ".join(r["flag_codes"]) if r["flag_codes"] else "(none)"
        marker = ""
        if r["true_label"] == "benign" and r["detected"]:
            marker = " <-- FP"
        elif r["true_label"] == "malicious" and not r["detected"]:
            marker = " <-- FN"
        print(f"{r['id']:<12} {r['true_label']:<12} {r['subset']:<16} {r['verdict']:<8} {codes}{marker}")

    return {
        "malicious_count": len(malicious),
        "benign_count": len(benign),
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "precision": precision,
        "recall": recall,
        "fp_by_code": fp_by_code,
        "all_results": all_results,
    }


def main():
    benign = _load_corpus("benign")
    adv_a = _load_corpus("adversarial_a")
    adv_b = _load_corpus("adversarial_b")

    print("Running detector over original corpus...")
    _print_corpus_report("ORIGINAL CORPUS", benign + adv_a + adv_b)

    # Holdout v2 corpus
    holdout = _load_corpus("holdout_v2")
    if holdout:
        print("\n\nRunning detector over holdout_v2 corpus...")
        _print_corpus_report("HOLDOUT V2", holdout)
    else:
        print("\nNo holdout_v2 corpus found.")

    # HTML corpus
    html_items = _load_corpus("html_v1")
    if html_items:
        print("\n\nRunning detector over HTML corpus...")
        _print_html_report(html_items)
    else:
        print("\nNo html_v1 corpus found.")


if __name__ == "__main__":
    main()
