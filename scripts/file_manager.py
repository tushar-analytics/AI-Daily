"""
FileManager: Handles all file read/write operations and repo structure.
"""

from pathlib import Path


class FileManager:
    def __init__(self, repo_root: Path):
        self.root = Path(repo_root)

        # Directories
        self.articles_dir = self.root / "articles"

        # Top-level files
        self.readme_file        = self.root / "README.md"
        self.facts_file         = self.root / "facts.md"
        self.interview_file     = self.root / "interview-questions.md"
        self.code_examples_file = self.root / "code-examples.md"
        self.diagrams_file      = self.root / "diagrams.md"
        self.quizzes_file       = self.root / "quizzes.md"
        self.summaries_file     = self.root / "summaries.md"

        # Ensure required directories exist
        self.articles_dir.mkdir(parents=True, exist_ok=True)

    # ── I/O ───────────────────────────────────────────────────────────────────

    def write(self, path: Path, content: str) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"  📄 Written: {path.relative_to(self.root)}")

    def read(self, path: Path) -> str:
        path = Path(path)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    # ── Repo introspection ────────────────────────────────────────────────────

    def list_articles(self) -> list[Path]:
        return sorted(self.articles_dir.glob("*.md"))

    def existing_topics(self) -> list[str]:
        return [p.stem.replace("-", " ").title() for p in self.list_articles()]

    def get_stats(self) -> dict:
        return {
            "articles": len(self.list_articles()),
        }
