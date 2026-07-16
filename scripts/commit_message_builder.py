"""
CommitMessageBuilder: Constructs unique, descriptive commit messages.

Now accepts the shared seeded Random instance so all randomness
in the run is reproducible from the same seed.
Duplicate detection is enforced via a `used_messages` set passed in
from the caller.
"""

import random as _random_module
import datetime
from typing import Optional


# ── Templates ─────────────────────────────────────────────────────────────────
# Each list gives several phrasings for the same intent.
# Having multiple variants per type avoids repeated messages on days with
# many updates of the same kind.

_TEMPLATES: dict[str, list[str]] = {
    "new_article": [
        "Add new article on {topic}",
        "Publish article: {topic}",
        "New article: {topic}",
        "Write article covering {topic}",
        "Draft and publish: {topic}",
    ],
    "expand_article": [
        "Expand {topic} article",
        "Extend notes on {topic}",
        "Add depth to {topic} guide",
        "Improve coverage of {topic}",
        "Enrich {topic} article with new section",
    ],
    "add_ai_facts": [
        "Add AI facts: {topic}",
        "Update facts: {topic}",
        "Add interesting AI facts on {topic}",
        "Curate new facts about {topic}",
        "Fact update: {topic}",
    ],
    "add_interview_questions": [
        "Add interview questions: {topic}",
        "Expand interview prep: {topic}",
        "Add ML interview Q&A: {topic}",
        "New interview section: {topic}",
        "Grow interview bank with {topic} questions",
    ],
    "add_python_examples": [
        "Add Python examples: {topic}",
        "Add code examples for {topic}",
        "Update code section: {topic}",
        "New Python snippets: {topic}",
        "Improve code examples covering {topic}",
    ],
    "add_mermaid_diagram": [
        "Add diagram: {topic}",
        "Add architecture diagram: {topic}",
        "Visualize {topic} with Mermaid",
        "New Mermaid diagram: {topic}",
        "Diagram added for {topic}",
    ],
    "update_readme": [
        "Update README with latest content",
        "Refresh README stats and index",
        "Sync README with new content",
        "Improve README index and badges",
        "README: reflect latest additions",
    ],
    "add_quiz": [
        "Add AI quiz: {topic}",
        "Update quiz section: {topic}",
        "Add knowledge quiz on {topic}",
        "New quiz: {topic}",
        "Extend quiz bank with {topic}",
    ],
    "add_summary": [
        "Add summary: {topic}",
        "Add cheat sheet: {topic}",
        "Quick-reference added: {topic}",
        "Publish concept summary: {topic}",
        "New summary card: {topic}",
    ],
}

_GENERIC_FALLBACKS = [
    "Daily AI content update",
    "Expand AI knowledge base",
    "AI-Daily: daily knowledge refresh",
    "Routine AI content improvements",
    "Knowledge base update",
]


class CommitMessageBuilder:
    def __init__(self, rng: _random_module.Random | None = None):
        self._rng = rng or _random_module.Random()

    # ── Public API ─────────────────────────────────────────────────────────────

    def build_single(self, result: dict, used_messages: set[str]) -> str:
        """
        Build a commit message for a single result dict.
        Guarantees the returned message is not in `used_messages`.
        Falls back to appending a date stamp if all templates are exhausted.
        """
        utype  = result.get("type", "")
        topic  = result.get("topic", "AI")
        # If the script already computed a specific commit_part, respect it
        # but still deduplicate.
        preferred = result.get("commit_part", "")

        candidates = self._candidates(utype, topic, preferred)
        for msg in candidates:
            if msg not in used_messages:
                return msg

        # Last resort: append today's date to force uniqueness
        base = candidates[0] if candidates else "Update AI content"
        stamped = f"{base} [{datetime.date.today().isoformat()}]"
        return stamped

    # ── Internals ──────────────────────────────────────────────────────────────

    def _candidates(self, utype: str, topic: str, preferred: str) -> list[str]:
        """Return an ordered list of candidate messages (most preferred first)."""
        candidates: list[str] = []

        if preferred:
            candidates.append(preferred)

        templates = list(_TEMPLATES.get(utype, []))
        self._rng.shuffle(templates)
        for tmpl in templates:
            candidates.append(tmpl.format(topic=topic))

        # Append generic fallbacks as last resort
        fallbacks = list(_GENERIC_FALLBACKS)
        self._rng.shuffle(fallbacks)
        candidates.extend(fallbacks)

        return candidates
