"""
CommitMessageBuilder: Constructs descriptive commit messages.
"""

import random
import datetime


# Prefix templates by update type
_TEMPLATES = {
    "new_article":             ["Add new article on {topic}", "Publish article: {topic}", "New article: {topic}"],
    "expand_article":          ["Expand {topic} article", "Extend notes on {topic}", "Add depth to {topic} guide"],
    "add_ai_facts":            ["Add AI facts: {topic}", "Update facts: {topic}", "Add interesting AI facts on {topic}"],
    "add_interview_questions": ["Add interview questions: {topic}", "Expand interview prep: {topic}", "Add ML interview Q&A: {topic}"],
    "add_python_examples":     ["Add Python examples: {topic}", "Add code examples for {topic}", "Update code section: {topic}"],
    "add_mermaid_diagram":     ["Add diagram: {topic}", "Add architecture diagram: {topic}", "Visualize {topic} with Mermaid"],
    "update_readme":           ["Update README with latest content", "Refresh README stats and index", "Sync README with new content"],
    "add_quiz":                ["Add AI quiz: {topic}", "Update quiz section: {topic}", "Add knowledge quiz on {topic}"],
    "add_summary":             ["Add summary: {topic}", "Add cheat sheet: {topic}", "Quick-reference added: {topic}"],
}

_GENERIC_PREFIXES = [
    "🤖 Daily AI content update",
    "📚 Expand AI knowledge base",
    "✨ AI-Daily: daily knowledge refresh",
]


class CommitMessageBuilder:
    def build(self, commit_parts: list[str], results: list[dict]) -> str:
        if not commit_parts:
            return f"🤖 Daily AI content update — {datetime.date.today().isoformat()}"

        if len(commit_parts) == 1:
            # Single update — use rich template if possible
            r = results[0] if results else {}
            return self._format_single(r)

        # Multiple updates — compose a multi-line message
        title = self._multi_title(results)
        body_lines = []
        for r in results:
            part = self._format_single(r, short=True)
            body_lines.append(f"- {part}")

        return title + "\n\n" + "\n".join(body_lines)

    def _format_single(self, result: dict, short: bool = False) -> str:
        utype = result.get("type", "")
        topic = result.get("topic", "AI")
        commit_part = result.get("commit_part", "")

        if commit_part:
            return commit_part

        templates = _TEMPLATES.get(utype, [])
        if templates:
            tmpl = random.choice(templates)
            return tmpl.format(topic=topic)

        return result.get("description", "Update AI content")

    def _multi_title(self, results: list[dict]) -> str:
        types = {r.get("type") for r in results}
        if "new_article" in types and "update_readme" in types:
            return "Add new AI article and update README"
        if "add_interview_questions" in types and "add_python_examples" in types:
            return "Expand interview prep with Q&A and code examples"
        if "add_ai_facts" in types and "add_quiz" in types:
            return "Add AI facts and quiz section"
        return random.choice(_GENERIC_PREFIXES) + f" ({len(results)} updates)"
