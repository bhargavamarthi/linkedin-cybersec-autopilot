# LinkedIn Cybersec Autopilot

A fully automated content pipeline that researches, writes, illustrates, and publishes cybersecurity posts to LinkedIn — three times a week, with no human in the loop. It runs on a GitHub Actions cron schedule, uses Claude to write grounded, fact-based posts, generates a matching image for free, and posts directly to LinkedIn via its API. Every post is archived back into the repo for a full history.

Live since April 2026 — 34+ posts published and archived to date.

## How it works

```
GitHub Actions (cron: Mon/Wed/Fri 9am UTC)
        │
        ▼
scripts/research.py   → Claude (Anthropic API) picks a topic by day-of-week,
                         writes a ~1200-char LinkedIn post + an image prompt
        │
        ▼
scripts/gen_image.py  → Pollinations.ai (FLUX model, free, no API key) renders
                         the accompanying image from that prompt
        │
        ▼
scripts/publish.py    → Posts text + image to LinkedIn via the UGC Posts API
        │
        ▼
posts/YYYY-MM-DD/      → post.json, image.jpg, and receipt.json are committed
                         back to the repo as a permanent archive
```

Each step is a separate script/workflow step, so a failure at any stage (e.g. image generation) degrades gracefully — `gen_image.py` falls back to a generic cybersecurity graphic, and if that fails too, `publish.py` just posts text-only.

## Content strategy

Topics rotate by day of week (`TOPIC_ROTATION` in `research.py`):

| Day | Post type | Focus |
|---|---|---|
| Monday | `threat_of_week` | The most talked-about breach, CVE, or ransomware incident from the past 7 days |
| Wednesday | `concept_explainer` | A cybersecurity concept explained in plain English |
| Friday | `industry_insight` | A regulatory shift or strategic trend (NIS2, AI-assisted attacks, CISA KEV, supply chain security, etc.) |

The system prompt explicitly constrains Claude to write as a 20+ year practitioner analyzing **real, named, verifiable facts** (CVEs, incidents, published research, statistics) in first person — and to never fabricate personal anecdotes, certification struggles, or confession-style hooks. Each post ends with a question or CTA to drive engagement, and ships with curated hashtags and an image prompt tailored to the topic.

## Repository structure

```
.github/workflows/
  post.yml            Main pipeline — runs Mon/Wed/Fri 9am UTC, or on demand
  token-check.yml      Weekly LinkedIn token health check (Mondays 8am UTC)
scripts/
  research.py          Claude writes the post + image prompt → posts/YYYY-MM-DD/post.json
  gen_image.py          Pollinations.ai (FLUX) generates the image → posts/YYYY-MM-DD/image.jpg
  publish.py            Publishes to LinkedIn via the UGC Posts API
posts/YYYY-MM-DD/       Archive of every generated post (text, image, publish receipt)
setup.sh                One-shot WSL2 setup script (system deps, venv, .env template)
CLAUDE.md               Project instructions read automatically by Claude Code
INSTALL_GUIDE.md        Full walkthrough: install Claude Code → configure → activate
GET_LINKEDIN_TOKEN.md   How to obtain a LinkedIn API token and person URN
```

## Automation & reliability

- **Scheduled runs** — `post.yml` fires every Monday, Wednesday, and Friday at 9am UTC via cron, with `workflow_dispatch` for manual runs from the Actions tab.
- **Self-archiving** — after every run, the bot commits the day's post, image, and receipt straight back into `posts/`, so the repo doubles as a content history.
- **Failure alerts** — if any pipeline step fails, a GitHub issue is opened automatically with a link to the failed run.
- **Token health monitoring** — `token-check.yml` pings LinkedIn's `userinfo` endpoint every Monday morning (before the post job runs) and opens an issue with step-by-step refresh instructions if the access token has expired or gone invalid.

## Setup

Full instructions live in `INSTALL_GUIDE.md` and `GET_LINKEDIN_TOKEN.md`; short version:

1. **Install Claude Code** (macOS/Windows/Linux installers, or npm) and authenticate with an Anthropic account.
2. **Clone this repo** and open it with `claude` — `CLAUDE.md` gives Claude full project context automatically.
3. **Run setup**: ask Claude Code to run `setup.sh`, which installs system packages, creates a Python venv, installs dependencies (`anthropic`, `requests`, `python-dotenv`, etc.), and scaffolds a `.env` file.
4. **Fill in credentials** in `.env`:
   - `ANTHROPIC_API_KEY` — from console.anthropic.com
   - `LINKEDIN_ACCESS_TOKEN` — see `GET_LINKEDIN_TOKEN.md` (expires every 60 days)
   - `LINKEDIN_PERSON_URN` — from the LinkedIn `userinfo` endpoint
5. **Test locally**: run `research.py` and `gen_image.py` to preview a post before publishing anything.
6. **Add the same secrets** to the repo under Settings → Secrets and variables → Actions.
7. **Push** — the workflow activates and runs automatically on the Mon/Wed/Fri schedule (or trigger it manually from the Actions tab).

### Running locally (WSL2 recommended)

```bash
source venv/bin/activate
set -a && source .env && set +a
python scripts/research.py
python scripts/gen_image.py
python scripts/publish.py
```

`CLAUDE.md` notes this project is developed on WSL2 (Ubuntu) on Windows — commands should be run from the WSL2 terminal, not PowerShell/CMD, and the project should live under the Linux home filesystem (`~/`) rather than `/mnt/c/...` for performance.

## Cost

| Service | Free tier | Typical usage |
|---|---|---|
| GitHub Actions | 2,000 min/month | ~36 min/month |
| Image generation (Pollinations.ai) | Free, no key | 3 requests/week |
| LinkedIn API | Free | Unlimited posts |
| Anthropic API | Pay per token | ~$0.01–0.05/post (~$0.50–2/month) |

The only real recurring cost is Anthropic API usage for `research.py` — already covered if you have a Claude Pro/Max plan.

## Example generated post

From `posts/2026-09-18/post.json` (`industry_insight`, Friday rotation):

> As of September 2026, the EU's NIS2 Directive enforcement enters full effect across member states. Organizations face concrete deadlines for asset inventories, supply chain risk assessments, and incident response protocols — with financial penalties tied to revenue percentages that rival GDPR fines...
>
> How are you approaching supply chain control verification — third-party audit results, self-assessments, or a hybrid model?

Each `post.json` also stores the topic, full hashtag set, the image prompt sent to FLUX, the post type, and the date — making every past post fully reproducible and auditable.

## Maintenance notes

- LinkedIn access tokens expire every 60 days — `token-check.yml` will flag this automatically, but keep an eye out for the health-check issue and refresh via `GET_LINKEDIN_TOKEN.md`.
- Never commit `.env` — it's already excluded via `.gitignore`.
- Avoid running `publish.py` twice in the same day (per `CLAUDE.md`) to prevent duplicate posts.
