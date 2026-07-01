# 🚀 AI-Daily Setup Guide

This guide walks you through the **one-time setup** needed to fully automate your AI-Daily repository.

---

## Prerequisites

- A GitHub account
- A Google AI Studio account (for Gemini API key — **free tier available**)

---

## Step 1: Create the GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Name the repository: **AI-Daily**
3. Set visibility to **Public** (required for free GitHub Actions minutes on public repos)
4. **Do NOT** initialize with a README (you'll push this project instead)
5. Click **Create repository**

---

## Step 2: Get a Gemini API Key

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **Get API Key** → **Create API key**
3. Copy the key (starts with `AIza...`)

> **Free tier:** Gemini 2.0 Flash has a generous free quota (60 requests/minute, 1500/day) — more than enough for daily updates.

---

## Step 3: Add the API Key to GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add:
   - **Name:** `GEMINI_API_KEY`
   - **Value:** `AIza...` (your key from Step 2)
5. Click **Add secret**

---

## Step 4: (Optional) Attribute Commits to Your Account

To make commits appear in your GitHub contribution graph:

1. In **Settings** → **Secrets and variables** → **Actions** → **Variables** tab
2. Click **New repository variable** and add:

   | Variable | Value |
   |----------|-------|
   | `GIT_EMAIL` | `your-github-email@example.com` |
   | `GIT_NAME` | `Your Name` |

> ⚠️ The email must match your GitHub account email for commits to appear in your contribution graph.

---

## Step 5: Push the Code to GitHub

In your terminal, run:

```bash
cd "d:\Resume ATS Grow\Github Automation\AI-Daily"

git init
git add .
git commit -m "🎉 Initial setup: AI-Daily automation"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/AI-Daily.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

---

## Step 6: Enable GitHub Actions

1. Go to your repository → **Actions** tab
2. If prompted, click **I understand my workflows, go ahead and enable them**
3. The workflow will run automatically at midnight UTC every day

---

## Step 7: (Optional) Test a Manual Run

1. Go to **Actions** → **🤖 AI-Daily Auto Update**
2. Click **Run workflow**
3. Optionally enter a number (1-6) for forced updates, or leave blank for random
4. Click **Run workflow**

Watch the logs — it should generate content and push a commit! ✅

---

## Workflow Schedule

The workflow is scheduled with:

```yaml
- cron: '0 0 * * *'   # Runs at 00:00 UTC daily
```

Plus a **random sleep (0–3600 seconds)** inside the job to vary the effective run time each day.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Workflow fails with API error | Verify `GEMINI_API_KEY` is set correctly in Secrets |
| No commits appearing | Check that `GIT_EMAIL` matches your GitHub email |
| "Permission denied" on push | Ensure `contents: write` is in the workflow permissions |
| Workflow not triggering | Check Actions tab is enabled; cron only runs on default branch |

---

## Cost

- **GitHub Actions:** Free for public repos (unlimited minutes)
- **Gemini API:** Free tier is sufficient (~10 API calls/day max)

**Total cost: $0/month** 🎉

---

## File Structure

```
AI-Daily/
├── .github/
│   └── workflows/
│       └── daily-update.yml     # GitHub Actions workflow
├── scripts/
│   ├── daily_update.py          # Main orchestrator
│   ├── content_engine.py        # Gemini AI content generator
│   ├── file_manager.py          # File read/write operations
│   ├── commit_message_builder.py # Descriptive commit messages
│   └── requirements.txt         # Python dependencies
├── articles/                    # Generated AI articles (auto-created)
├── facts.md                     # Daily AI facts
├── interview-questions.md       # Interview Q&A
├── code-examples.md             # Python code examples
├── diagrams.md                  # Mermaid diagrams
├── quizzes.md                   # Knowledge quizzes
├── summaries.md                 # Concept summaries
├── README.md                    # Auto-updated index
└── SETUP.md                     # This file
```
