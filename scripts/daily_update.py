"""
AI-Daily: Daily AI content update orchestrator.

New behaviour:
  - N is drawn from [0, 8] with a date-seeded RNG.
  - N = 0  → exit cleanly, no commits.
  - N > 0  → run N updates; each successful update is committed
              individually with a unique, descriptive commit message.
  - Failures are isolated: a broken update is skipped and the rest continue.
"""

import os
import random
import hashlib
import subprocess
import datetime
import sys
from pathlib import Path

# Add scripts dir to path so sibling imports work
sys.path.insert(0, str(Path(__file__).parent))

from content_engine import ContentEngine
from file_manager import FileManager
from commit_message_builder import CommitMessageBuilder


# ── RNG seed ──────────────────────────────────────────────────────────────────

def build_seed() -> int:
    """
    Build a deterministic but unique seed for today's run.

    Combines today's date with the GitHub run-id (injected as RUN_DATE env var)
    so that:
      - Different days always produce different sequences.
      - A manual re-run of the same workflow run-id is reproducible.
      - No two consecutive days are identical.
    """
    today = datetime.date.today().isoformat()          # e.g. "2026-07-16"
    run_id = os.environ.get("RUN_DATE", "0")            # GitHub run_id
    raw = f"{today}-{run_id}"
    # MD5 hex → int (plenty of entropy, not used for security)
    return int(hashlib.md5(raw.encode()).hexdigest(), 16)


# ── N selection ───────────────────────────────────────────────────────────────

def get_num_updates(rng: random.Random) -> int:
    """
    Return N ∈ [0, 8].

    Distribution rationale
    ----------------------
    0  → ~12 % (skip day — keeps the history varied, not robotic)
    1  → ~8 %
    2  → ~15 %
    3  → ~20 %
    4  → ~20 %
    5  → ~13 %
    6  → ~7 %
    7  → ~4 %
    8  → ~1 %
    """
    forced = os.environ.get("FORCE_UPDATES", "").strip()
    if forced and forced.lstrip("-").isdigit():
        return max(0, min(8, int(forced)))

    weights = [12, 8, 15, 20, 20, 13, 7, 4, 1]   # index 0..8
    return rng.choices(range(9), weights=weights)[0]


# ── Update type selection ─────────────────────────────────────────────────────

_UPDATE_POOL = [
    ("new_article",             20),
    ("expand_article",          18),
    ("add_ai_facts",            15),
    ("add_interview_questions", 14),
    ("add_python_examples",     13),
    ("add_mermaid_diagram",     10),
    ("update_readme",            5),
    ("add_quiz",                 3),
    ("add_summary",              2),
]


def pick_unique_update_types(n: int, rng: random.Random) -> list[str]:
    """Pick n unique update types using weighted sampling without replacement."""
    remaining = list(_UPDATE_POOL)
    chosen = []
    for _ in range(min(n, len(remaining))):
        pool, weights = zip(*remaining)
        pick = rng.choices(pool, weights=weights, k=1)[0]
        chosen.append(pick)
        remaining = [(p, w) for p, w in remaining if p != pick]
    return chosen


# ── Git helpers ───────────────────────────────────────────────────────────────

def git_commit(repo_root: Path, message: str) -> bool:
    """Stage all changes and commit with the given message. Returns True on success."""
    try:
        # Stage everything
        subprocess.run(
            ["git", "add", "-A"],
            cwd=repo_root, check=True, capture_output=True
        )
        # Check if there is anything to commit
        status = subprocess.run(
            ["git", "diff", "--staged", "--quiet"],
            cwd=repo_root, capture_output=True
        )
        if status.returncode == 0:
            print("  ⚠️  Nothing staged to commit — skipping.")
            return False

        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_root, check=True, capture_output=True
        )
        print(f"  ✅ Committed: {message!r}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ git commit failed: {e.stderr.decode().strip()}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("🤖 AI-Daily update started")
    repo_root = Path(__file__).parent.parent

    # ── Seed RNG ──
    seed = build_seed()
    rng = random.Random(seed)
    print(f"🎲 RNG seed: {seed & 0xFFFFFFFF:#010x}  (date: {datetime.date.today().isoformat()})")

    # ── Decide N ──
    num_updates = get_num_updates(rng)
    print(f"📋 N = {num_updates}")

    if num_updates == 0:
        print("🛑 N = 0 → skipping today. No changes will be made.")
        _write_summary([], 0, skipped=True, repo_root=repo_root)
        sys.exit(0)

    # ── Pick update types ──
    update_types = pick_unique_update_types(num_updates, rng)
    print(f"📋 Update plan: {update_types}")

    # ── Initialise helpers ──
    engine = ContentEngine(rng=rng)
    fm = FileManager(repo_root)
    cmb = CommitMessageBuilder(rng=rng)

    used_messages: set[str] = set()   # guard against duplicate commit messages
    results: list[dict] = []
    committed = 0

    for i, update_type in enumerate(update_types, 1):
        print(f"\n▶ [{i}/{num_updates}] Running: {update_type}")
        try:
            result = engine.run_update(update_type, fm)
            msg = cmb.build_single(result, used_messages)
            used_messages.add(msg)

            if git_commit(repo_root, msg):
                committed += 1

            results.append(result)
            print(f"  📝 Message: {msg!r}")

        except Exception as exc:
            import traceback
            print(f"  ⚠️  Update '{update_type}' failed — continuing with next update.")
            traceback.print_exc()

    print(f"\n✅ Done. {committed}/{num_updates} update(s) committed.")
    _write_summary(results, committed, skipped=False, repo_root=repo_root)


def _write_summary(results: list[dict], committed: int, *, skipped: bool, repo_root: Path):
    lines = [
        f"**Date:** {datetime.date.today().isoformat()}",
        f"**Status:** {'⏭️ Skipped (N=0)' if skipped else f'✅ {committed} commit(s) made'}",
    ]
    if results:
        lines += [
            "",
            "| # | Type | Description |",
            "|---|------|-------------|",
        ]
        for i, r in enumerate(results, 1):
            lines.append(f"| {i} | `{r.get('type', '?')}` | {r.get('description', '-')} |")

    (repo_root / ".run_summary.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
