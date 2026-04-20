# LinkedIn Cybersec Autopilot — Claude Code Instructions

## Environment
WSL2 (Ubuntu) on Windows 11. Always run commands inside the WSL2 terminal.
Never run Python or Git from PowerShell/CMD.

## Architecture
GitHub Actions (cron) → research.py (Claude) → gen_image.py (Gemini) → publish.py (LinkedIn API)

## Key Files
- `.github/workflows/post.yml` — cron schedule (Mon/Wed/Fri 9am UTC)
- `scripts/research.py` — Claude writes post + image prompt
- `scripts/gen_image.py` — Gemini generates image
- `scripts/publish.py` — posts to LinkedIn via UGC Posts API
- `posts/YYYY-MM-DD/` — archive of all generated posts

## Secrets (set via: gh secret set NAME)
- ANTHROPIC_API_KEY
- GEMINI_API_KEY
- LINKEDIN_ACCESS_TOKEN  (expires every 60 days)
- LINKEDIN_PERSON_URN

## Run pipeline locally (WSL2)
```bash
source venv/bin/activate
set -a && source .env && set +a
python scripts/research.py
python scripts/gen_image.py
python scripts/publish.py
```

## View image from Windows
Open Windows Explorer and navigate to: \\wsl$\Ubuntu\home\USERNAME\linkedin-cybersec-autopilot\posts

## DO NOT
- Work from /mnt/c/... paths (slow — use ~/linux filesystem)
- Use sudo pip install (use venv instead)
- Commit .env to Git
- Run publish.py twice on the same day
