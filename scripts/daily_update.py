"""
AI-Daily: Daily AI content update orchestrator.
Runs inside GitHub Actions to generate and commit AI-related content.
"""

import os
import random
import json
import datetime
import sys
from pathlib import Path

from content_engine import ContentEngine
from file_manager import FileManager
from commit_message_builder import CommitMessageBuilder


def get_num_updates() -> int:
    """Return number of updates for today — random unless forced via env."""
    forced = os.environ.get("FORCE_UPDATES", "").strip()
    if forced and forced.isdigit():
        return max(1, min(6, int(forced)))
    # Weighted random: most days do 2-4 updates
    weights = [5, 20, 30, 25, 15, 5]   # 1 through 6
    return random.choices(range(1, 7), weights=weights)[0]


def pick_unique_update_types(n: int) -> list[str]:
    """Pick n unique update types, weighted by value."""
    update_types = [
        ("new_article",          20),
        ("expand_article",       18),
        ("add_ai_facts",         15),
        ("add_interview_questions", 14),
        ("add_python_examples",  13),
        ("add_mermaid_diagram",  10),
        ("update_readme",         5),
        ("add_quiz",              3),
        ("add_summary",           2),
    ]
    pool = [t for t, _ in update_types]
    weights = [w for _, w in update_types]

    chosen = []
    remaining_pool = list(zip(pool, weights))

    for _ in range(min(n, len(pool))):
        r_pool, r_weights = zip(*remaining_pool)
        pick = random.choices(r_pool, weights=r_weights, k=1)[0]
        chosen.append(pick)
        remaining_pool = [(p, w) for p, w in remaining_pool if p != pick]

    return chosen


def main():
    print("🤖 AI-Daily update started")
    repo_root = Path(__file__).parent.parent

    engine = ContentEngine()
    fm = FileManager(repo_root)
    cmb = CommitMessageBuilder()

    num_updates = get_num_updates()
    update_types = pick_unique_update_types(num_updates)

    print(f"📋 Planning {num_updates} update(s): {update_types}")

    results = []
    commit_parts = []

    for update_type in update_types:
        print(f"\n▶ Running: {update_type}")
        try:
            result = engine.run_update(update_type, fm)
            results.append(result)
            commit_parts.append(result.get("commit_part", update_type))
            print(f"  ✅ Done: {result.get('description', update_type)}")
        except Exception as e:
            print(f"  ⚠️  Failed ({update_type}): {e}")

    # Write commit message
    commit_msg = cmb.build(commit_parts, results)
    (repo_root / ".commit_message.txt").write_text(commit_msg, encoding="utf-8")
    print(f"\n📝 Commit message: {commit_msg}")

    # Write run summary for GitHub Actions job summary
    summary_lines = [
        f"**Date:** {datetime.date.today().isoformat()}",
        f"**Updates performed:** {len(results)} / {num_updates} planned",
        "",
        "| # | Type | Description |",
        "|---|------|-------------|",
    ]
    for i, r in enumerate(results, 1):
        summary_lines.append(f"| {i} | `{r.get('type', '?')}` | {r.get('description', '-')} |")

    (repo_root / ".run_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")

    print("\n✅ AI-Daily update complete!")


if __name__ == "__main__":
    main()
