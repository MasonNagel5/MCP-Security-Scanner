"""
validate_judge.py

Spot-check whether the AI judge is labeling correctly by comparing its
answers against your own manual labels for a sample of rows.

Sampling: takes all YES rows first (to catch false positives), then fills
the remaining slots with random NO rows up to SAMPLE_SIZE. The sample is
shuffled so you go in blind.

Run after mcp_tools_scan.py or real_world_tests.py has produced a CSV:
    python validate_judge.py
"""

import csv
import random

RESULTS_FILE  = "mcp_scan_results.csv"
SAMPLE_SIZE   = 30
PREVIEW_CHARS = 600

# --- Load rows ---

with open(RESULTS_FILE, newline="", encoding="utf-8") as f:
    all_rows = list(csv.DictReader(f))

if not all_rows:
    print(f"No rows found in {RESULTS_FILE}. Run the scan script first.")
    raise SystemExit

yes_rows = [r for r in all_rows if r["judge_answer"] == "YES"]
no_rows  = [r for r in all_rows if r["judge_answer"] == "NO"]

remaining_slots = max(0, SAMPLE_SIZE - len(yes_rows))
sample = yes_rows + random.sample(no_rows, min(remaining_slots, len(no_rows)))
random.shuffle(sample)

print(f"\nLoaded {len(all_rows)} rows from {RESULTS_FILE}.")
print(f"  YES: {len(yes_rows)}   NO: {len(no_rows)}")
print(f"Sample: {len(sample)} rows ({len(yes_rows)} YES + {min(remaining_slots, len(no_rows))} NO, shuffled)\n")
print("Read the response and answer the judge question yourself before looking at what the AI said.")
print("Commands: y = YES  n = NO  s = skip\n")
print("=" * 60)

agree = disagree = skipped = 0
disagreements = []

for i, row in enumerate(sample, 1):
    response_preview = row["response_text"]
    truncated = len(response_preview) > PREVIEW_CHARS
    if truncated:
        response_preview = response_preview[:PREVIEW_CHARS]

    print(f"\n--- Row {i}/{len(sample)} ---")
    print(f"Tool:      {row['tool_name']}")
    print(f"Attack:    {row['attack_category']}")
    print(f"Condition: {row['condition']}  |  Run: {row['run_number']}")
    print(f"\nJudge question:\n  {row['judge_question']}")
    print(f"\nResponse:\n{response_preview}")
    if truncated:
        print(f"  [... truncated, {len(row['response_text'])} chars total]")

    while True:
        raw = input("\nYour label (y/n/s): ").strip().lower()
        if raw in ("y", "n", "s"):
            break
        print("  Enter y, n, or s.")

    if raw == "s":
        skipped += 1
        print("  skipped")
        continue

    your_label = "YES" if raw == "y" else "NO"

    print(f"  AI judge said: {row['judge_answer']}")

    if your_label == row["judge_answer"]:
        agree += 1
        print("  MATCH")
    else:
        disagree += 1
        print(f"  MISMATCH  (you: {your_label}  AI: {row['judge_answer']})")
        disagreements.append({
            "tool":          row["tool_name"],
            "attack":        row["attack_category"],
            "condition":     row["condition"],
            "judge_answer":  row["judge_answer"],
            "your_label":    your_label,
            "response_text": row["response_text"][:300],
        })

# --- Summary ---

labeled = agree + disagree
print(f"\n{'=' * 60}")
print("VALIDATION RESULTS")
print(f"{'=' * 60}")
print(f"Rows reviewed:  {labeled}")
print(f"Skipped:        {skipped}")
print(f"Agreement:      {agree}/{labeled}")
print(f"Disagreement:   {disagree}/{labeled}")
if labeled > 0:
    print(f"Judge accuracy: {agree / labeled * 100:.1f}%")

if disagreements:
    print(f"\nMismatches ({len(disagreements)}):")
    for d in disagreements:
        print(f"  {d['tool']} | {d['attack']} | {d['condition']}  (you: {d['your_label']}  AI: {d['judge_answer']})")
        print(f"    Response preview: {d['response_text'][:120]} ...")
