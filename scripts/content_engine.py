"""
ContentEngine: Generates AI content using Gemini API.
Each update type calls a specific generation method.

The engine now accepts a seeded random.Random instance so every topic
pick and article selection is reproducible from the same daily seed.
"""

import os
import random as _random_module
import datetime
import re
from pathlib import Path

import google.generativeai as genai


# ── Topics pool ────────────────────────────────────────────────────────────────
AI_TOPICS = [
    "Retrieval-Augmented Generation (RAG)",
    "Large Language Models (LLMs)",
    "Prompt Engineering",
    "Fine-tuning vs In-context Learning",
    "Transformer Architecture",
    "Attention Mechanisms",
    "AI Agents and Agentic Workflows",
    "Vector Databases and Embeddings",
    "Chain-of-Thought Reasoning",
    "Constitutional AI and RLHF",
    "Multimodal AI Models",
    "AI Safety and Alignment",
    "Knowledge Graphs for AI",
    "Model Quantization and Pruning",
    "Mixture of Experts (MoE)",
    "Low-Rank Adaptation (LoRA)",
    "AI Ethics and Bias",
    "Graph Neural Networks",
    "Diffusion Models",
    "Reinforcement Learning from Human Feedback (RLHF)",
    "AI in Healthcare",
    "AI for Code Generation",
    "Federated Learning",
    "AI Hallucinations and Mitigation",
    "Semantic Search",
    "AI Memory Systems",
    "Tool-using AI (Function Calling)",
    "AI Benchmarks and Evaluation",
    "Zero-shot and Few-shot Learning",
    "Model Context Windows",
]


class ContentEngine:
    def __init__(self, rng: _random_module.Random | None = None):
        self._rng = rng or _random_module.Random()
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
            self.use_ai = True
        else:
            print("⚠️  No GEMINI_API_KEY found — using fallback static content.")
            self.use_ai = False

    # ── Public dispatcher ──────────────────────────────────────────────────────

    def run_update(self, update_type: str, fm) -> dict:
        dispatch = {
            "new_article":             self._new_article,
            "expand_article":          self._expand_article,
            "add_ai_facts":            self._add_ai_facts,
            "add_interview_questions": self._add_interview_questions,
            "add_python_examples":     self._add_python_examples,
            "add_mermaid_diagram":     self._add_mermaid_diagram,
            "update_readme":           self._update_readme,
            "add_quiz":                self._add_quiz,
            "add_summary":             self._add_summary,
        }
        handler = dispatch.get(update_type)
        if not handler:
            raise ValueError(f"Unknown update type: {update_type}")
        return handler(fm)

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _pick_topic(self, exclude: list[str] | None = None) -> str:
        pool = [t for t in AI_TOPICS if t not in (exclude or [])]
        return self._rng.choice(pool)

    def _generate(self, prompt: str, fallback: str) -> str:
        if not self.use_ai:
            return fallback
        try:
            resp = self.model.generate_content(prompt)
            return resp.text.strip()
        except Exception as e:
            print(f"  ⚠️  Gemini error: {e}")
            return fallback

    def _slug(self, topic: str) -> str:
        s = topic.lower()
        s = re.sub(r"[^a-z0-9\s-]", "", s)
        s = re.sub(r"\s+", "-", s.strip())
        return s

    def _today(self) -> str:
        return datetime.date.today().isoformat()

    # ── Update handlers ────────────────────────────────────────────────────────

    def _new_article(self, fm) -> dict:
        topic = self._pick_topic(exclude=fm.existing_topics())
        slug = self._slug(topic)
        prompt = f"""Write a comprehensive, well-structured Markdown article about "{topic}" for an AI learning repository.

Requirements:
- Title as H1
- 4-6 sections with H2 headings
- Include practical examples, key concepts, and real-world applications
- Include a "Key Takeaways" section at the end
- Use bullet points, code blocks, and bold text appropriately
- Length: 600-900 words
- Do NOT include front matter / YAML headers
"""
        fallback = f"# {topic}\n\n*Article coming soon.*\n"
        content = self._generate(prompt, fallback)
        date = self._today()
        full_content = f"---\ntitle: \"{topic}\"\ndate: {date}\ntags: [ai, learning]\n---\n\n{content}\n"
        path = fm.articles_dir / f"{slug}.md"
        fm.write(path, full_content)
        return {
            "type": "new_article",
            "description": f"New article: {topic}",
            "commit_part": f"Add new article on {topic}",
            "topic": topic,
        }

    def _expand_article(self, fm) -> dict:
        existing = fm.list_articles()
        if not existing:
            return self._new_article(fm)
        article_path = self._rng.choice(existing)
        topic = article_path.stem.replace("-", " ").title()
        existing_content = fm.read(article_path)
        prompt = f"""The following is an existing Markdown article about "{topic}".

EXISTING CONTENT:
{existing_content[:2000]}

Please add a new, meaningful section (H2) to this article. The section should:
- Be titled appropriately (e.g., "Advanced Techniques", "Common Pitfalls", "Industry Use Cases", etc.)
- Be 200-350 words
- Include practical insights not covered above
- Use bullet points, code examples, or diagrams where helpful

Return ONLY the new section markdown, starting with the ## heading.
"""
        fallback = f"\n## Additional Notes\n\nMore content about {topic} coming soon.\n"
        new_section = self._generate(prompt, fallback)
        updated = existing_content.rstrip() + "\n\n" + new_section + "\n"
        fm.write(article_path, updated)
        return {
            "type": "expand_article",
            "description": f"Expanded article: {topic}",
            "commit_part": f"Expand {topic} article",
            "topic": topic,
        }

    def _add_ai_facts(self, fm) -> dict:
        topic = self._pick_topic()
        prompt = f"""Generate 8 interesting, accurate, and surprising AI facts related to "{topic}".

Format as a Markdown list with bold fact titles followed by a brief explanation.
Example:
- **Fact title**: Explanation of the fact in 1-2 sentences.

Return only the list, no intro text.
"""
        fallback = f"- **AI is advancing**: New breakthroughs in {topic} happen regularly.\n"
        facts = self._generate(prompt, fallback)
        date = self._today()
        section = f"\n## {date} — Facts about {topic}\n\n{facts}\n"
        path = fm.facts_file
        existing = fm.read(path) if path.exists() else "# 🤖 AI Facts\n\nDaily AI facts and discoveries.\n"
        fm.write(path, existing.rstrip() + "\n" + section)
        return {
            "type": "add_ai_facts",
            "description": f"Added AI facts about {topic}",
            "commit_part": f"Add AI facts: {topic}",
        }

    def _add_interview_questions(self, fm) -> dict:
        topic = self._pick_topic()
        prompt = f"""Create 6 realistic AI interview questions about "{topic}" for a senior ML/AI engineer role.

For each question:
1. Write the question in bold
2. Provide a model answer (3-5 sentences, technically accurate)
3. Add a "💡 Pro tip:" hint

Format as Markdown. Return only the Q&A content, no intro.
"""
        fallback = f"**Q: What is {topic}?**\n\nA: {topic} is a key AI concept. More details coming soon.\n"
        content = self._generate(prompt, fallback)
        date = self._today()
        section = f"\n## {date} — Interview Questions: {topic}\n\n{content}\n"
        path = fm.interview_file
        existing = fm.read(path) if path.exists() else "# 🎯 AI Interview Questions\n\nCurated interview Q&A for AI/ML roles.\n"
        fm.write(path, existing.rstrip() + "\n" + section)
        return {
            "type": "add_interview_questions",
            "description": f"Added interview questions on {topic}",
            "commit_part": f"Add interview questions: {topic}",
        }

    def _add_python_examples(self, fm) -> dict:
        topic = self._pick_topic()
        prompt = f"""Write 2 practical, well-commented Python code examples demonstrating "{topic}".

Requirements:
- Use realistic, runnable Python code (Python 3.10+)
- Include comments explaining key lines
- Use common libraries (transformers, openai, langchain, torch, sklearn, etc.)
- Each example should have a brief intro paragraph
- Format as Markdown code blocks with ```python
- Keep each example 20-40 lines

Return only the Markdown content with examples.
"""
        fallback = f"```python\n# Example for {topic}\nprint('Hello, {topic}!')\n```\n"
        content = self._generate(prompt, fallback)
        date = self._today()
        section = f"\n## {date} — Python Examples: {topic}\n\n{content}\n"
        path = fm.code_examples_file
        existing = fm.read(path) if path.exists() else "# 🐍 Python Code Examples\n\nPractical Python examples for AI concepts.\n"
        fm.write(path, existing.rstrip() + "\n" + section)
        return {
            "type": "add_python_examples",
            "description": f"Added Python examples for {topic}",
            "commit_part": f"Add Python examples: {topic}",
        }

    def _add_mermaid_diagram(self, fm) -> dict:
        topic = self._pick_topic()
        prompt = f"""Create a Mermaid diagram that visually explains "{topic}".

Requirements:
- Use an appropriate diagram type (flowchart, sequenceDiagram, classDiagram, stateDiagram, etc.)
- The diagram should clearly show the key components and their relationships
- Add a brief 2-3 sentence explanation before the diagram
- Format as Markdown with a ```mermaid code block

Return only the explanation + mermaid block, no extra text.
"""
        fallback = f"```mermaid\ngraph TD\n    A[{topic}] --> B[Core Concept]\n    B --> C[Application]\n```\n"
        content = self._generate(prompt, fallback)
        date = self._today()
        section = f"\n## {date} — Diagram: {topic}\n\n{content}\n"
        path = fm.diagrams_file
        existing = fm.read(path) if path.exists() else "# 📊 AI Architecture Diagrams\n\nMermaid diagrams explaining AI concepts.\n"
        fm.write(path, existing.rstrip() + "\n" + section)
        return {
            "type": "add_mermaid_diagram",
            "description": f"Added Mermaid diagram for {topic}",
            "commit_part": f"Add diagram: {topic}",
        }

    def _update_readme(self, fm) -> dict:
        articles = fm.list_articles()
        article_list = "\n".join(
            f"- [{p.stem.replace('-', ' ').title()}](articles/{p.name})"
            for p in sorted(articles)[:20]
        )
        date = self._today()
        stats = fm.get_stats()
        readme_content = f"""# 🤖 AI-Daily

> **Automatically updated every day** with AI articles, facts, interview questions, code examples, and more.
> Powered by Gemini AI + GitHub Actions.

![Last Updated](https://img.shields.io/badge/Last%20Updated-{date}-blue?style=flat-square)
![Articles](https://img.shields.io/badge/Articles-{stats['articles']}-green?style=flat-square)
![Auto Updated](https://img.shields.io/badge/Auto%20Updated-Daily-orange?style=flat-square)

---

## 📚 What's Inside

| Resource | Description |
|----------|-------------|
| [📰 Articles](articles/) | In-depth AI articles generated daily |
| [💡 AI Facts](facts.md) | Surprising and interesting AI facts |
| [🎯 Interview Questions](interview-questions.md) | Real ML/AI interview Q&A |
| [🐍 Code Examples](code-examples.md) | Practical Python AI examples |
| [📊 Diagrams](diagrams.md) | Mermaid diagrams of AI architectures |
| [🧠 Quizzes](quizzes.md) | Test your AI knowledge |
| [📋 Summaries](summaries.md) | Concise concept summaries |

---

## 📰 Recent Articles

{article_list if article_list else "_No articles yet — check back tomorrow!_"}

---

## ⚙️ How It Works

```mermaid
flowchart LR
    A[⏰ GitHub Actions\nDaily Trigger] --> B[🎲 Random 1-6 Updates]
    B --> C[🤖 Gemini AI\nContent Generation]
    C --> D[📝 Write Files]
    D --> E[✅ Auto Commit\n& Push]
```

1. **GitHub Actions** triggers the workflow every day at midnight UTC
2. A **random delay** (0–60 min) is applied to vary the actual run time
3. The script picks **1–6 random update types** using weighted randomness
4. **Gemini AI** generates high-quality, unique content
5. Changes are committed with **descriptive messages** and pushed automatically

---

## 🚀 Setup (One-time)

See [SETUP.md](SETUP.md) for full configuration instructions.

---

## 📈 Statistics

- **Total Articles:** {stats['articles']}
- **Last Updated:** {date}
- **Auto-updates:** Daily ♻️

---

*This repository is 100% automated. All content is AI-generated for educational purposes.*
"""
        fm.write(fm.readme_file, readme_content)
        return {
            "type": "update_readme",
            "description": "Updated README with latest stats and article list",
            "commit_part": "Update README with latest content",
        }

    def _add_quiz(self, fm) -> dict:
        topic = self._pick_topic()
        prompt = f"""Create a 5-question multiple-choice quiz about "{topic}" for AI learners.

For each question:
1. Write a clear question
2. Provide 4 options (A, B, C, D)
3. Indicate the correct answer with **Answer: X**
4. Add a 1-sentence explanation

Format as Markdown. Return only the quiz content.
"""
        fallback = f"**Q1: What is {topic}?**\nA) Option A  B) Option B  C) Option C  D) Option D\n**Answer: A**\n"
        content = self._generate(prompt, fallback)
        date = self._today()
        section = f"\n## {date} — Quiz: {topic}\n\n{content}\n"
        path = fm.quizzes_file
        existing = fm.read(path) if path.exists() else "# 🧠 AI Knowledge Quizzes\n\nTest your AI knowledge with daily quizzes.\n"
        fm.write(path, existing.rstrip() + "\n" + section)
        return {
            "type": "add_quiz",
            "description": f"Added quiz on {topic}",
            "commit_part": f"Add AI quiz: {topic}",
        }

    def _add_summary(self, fm) -> dict:
        topic = self._pick_topic()
        prompt = f"""Write a concise, structured summary of "{topic}" for a developer cheat sheet.

Format:
## {topic}

**What it is:** One sentence definition.

**Why it matters:** 2-3 bullet points.

**Key concepts:**
- Concept 1: brief explanation
- Concept 2: brief explanation
- Concept 3: brief explanation

**Quick example:** A 5-10 line code snippet or formula.

**Further reading:** 2-3 suggested search terms or resource names (no URLs needed).

Return only the Markdown content above.
"""
        fallback = f"## {topic}\n\n**What it is:** A key AI concept.\n"
        content = self._generate(prompt, fallback)
        date = self._today()
        section = f"\n<!-- {date} -->\n{content}\n"
        path = fm.summaries_file
        existing = fm.read(path) if path.exists() else "# 📋 AI Concept Summaries\n\nQuick-reference summaries for key AI concepts.\n"
        fm.write(path, existing.rstrip() + "\n" + section)
        return {
            "type": "add_summary",
            "description": f"Added summary for {topic}",
            "commit_part": f"Add summary: {topic}",
        }
