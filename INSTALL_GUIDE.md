# Claude Code Installation & Project Setup Guide
## LinkedIn Cybersec Autopilot

---

## Part 1 — Install Claude Code on Your Laptop

### macOS (Recommended — Native Installer)

Open **Terminal** and run:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Verify:
```bash
claude --version
```

**Alternative (Homebrew):**
```bash
brew install claude-code
```

---

### Windows (Native Installer — No Node.js needed)

1. Open **PowerShell** (search Start menu → "PowerShell")
2. Run:
```powershell
irm https://claude.ai/install.ps1 | iex
```
3. Verify:
```powershell
claude --version
```

> ⚠️ If you see `'irm' is not recognized` you are in CMD, not PowerShell.
> If you see `The token '&&' is not a valid statement separator` you are in PowerShell not CMD — that's fine, the command above works there.

**Alternative (WinGet):**
```powershell
winget install Anthropic.ClaudeCode
```

---

### Linux (Native Installer)

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

If you prefer npm (Node.js 18+ required):
```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
npm install -g @anthropic-ai/claude-code
```

---

## Part 2 — Authenticate Claude Code

After installing, run:

```bash
claude
```

You will be prompted to log in with your Anthropic account.
- Use your existing Claude.ai account credentials, OR
- Create a free account at https://claude.ai

> **Note:** Claude Code uses your Anthropic API credits. If you have a Claude Pro/Max plan, usage is included. Otherwise, you'll need to add billing at https://console.anthropic.com

---

## Part 3 — Set Up the LinkedIn Cybersec Autopilot Project

### 3A. Clone or create the GitHub repo

**Option A — Clone the repo you downloaded:**
```bash
cd ~/Documents
git clone https://github.com/YOUR-USERNAME/linkedin-cybersec-autopilot
cd linkedin-cybersec-autopilot
```

**Option B — Create from the downloaded ZIP:**
```bash
cd ~/Documents
unzip linkedin-cybersec-autopilot.zip
cd linkedin-cybersec-autopilot
git init
git add .
git commit -m "Initial setup"
```

Then create a GitHub repo at https://github.com/new and push:
```bash
git remote add origin https://github.com/YOUR-USERNAME/linkedin-cybersec-autopilot.git
git branch -M main
git push -u origin main
```

---

### 3B. Open in Claude Code

```bash
cd linkedin-cybersec-autopilot
claude
```

Claude Code will read `CLAUDE.md` automatically and understand your entire project.

---

### 3C. Run setup via Claude Code

Inside the Claude Code session, type:

```
run the setup script to install dependencies and create my .env file
```

Claude Code will run `bash setup.sh` for you. Then fill in `.env`:

```
ANTHROPIC_API_KEY=sk-ant-...      ← from console.anthropic.com
GEMINI_API_KEY=AIza...            ← from aistudio.google.com/apikey (free)
LINKEDIN_ACCESS_TOKEN=...         ← see GET_LINKEDIN_TOKEN.md
LINKEDIN_PERSON_URN=urn:li:person:...
```

---

### 3D. Test the pipeline locally

Ask Claude Code:

```
run the full pipeline in test mode — research a topic, generate the image prompt,
but do NOT publish to LinkedIn yet. Show me the output.
```

Claude Code will run:
1. `python scripts/research.py` → creates `posts/YYYY-MM-DD/post.json`
2. `python scripts/gen_image.py` → creates `posts/YYYY-MM-DD/image.png`

Review `posts/YYYY-MM-DD/post.json` — if you like it, then:

```
now publish to LinkedIn
```

---

### 3E. Add secrets to GitHub

1. Go to: `https://github.com/YOUR-USERNAME/linkedin-cybersec-autopilot/settings/secrets/actions`
2. Click **New repository secret** for each:
   - `ANTHROPIC_API_KEY`
   - `GEMINI_API_KEY`
   - `LINKEDIN_ACCESS_TOKEN`
   - `LINKEDIN_PERSON_URN`

---

### 3F. Push and activate GitHub Actions

```bash
git add .
git commit -m "Add secrets and activate pipeline"
git push
```

Go to your repo → **Actions** tab → you'll see the workflow.
It will auto-run every **Monday, Wednesday, Friday at 9am UTC**.

To run it manually: Actions → "LinkedIn Cybersec Autopilot" → **Run workflow**

---

## Useful Claude Code Commands (inside your project)

| What you type | What Claude Code does |
|---|---|
| `show me today's generated post` | Reads and displays `posts/YYYY-MM-DD/post.json` |
| `edit the post to be more conversational` | Rewrites and saves the post |
| `change the posting schedule to daily` | Updates the cron in `.github/workflows/post.yml` |
| `why did the last GitHub Action fail?` | Reads workflow logs and explains the error |
| `add a new topic type: tool review` | Adds a new post type to `research.py` |
| `show me all posts from this month` | Lists the posts archive |

---

## Cost Summary

| Service | Free Tier | Usage |
|---|---|---|
| GitHub Actions | 2,000 min/month | ~36 min/month used |
| Gemini Pro | 1,500 requests/day | 3 requests/week |
| LinkedIn API | Free | Unlimited posts |
| Anthropic API | Pay per token | ~$0.01–0.05 per post |

> The only actual cost is the Anthropic API calls (~$0.50–2/month for 12 posts).
> If you have Claude Pro ($20/mo), API access may already be included.

---

## Troubleshooting

**`claude: command not found` after install**
```bash
source ~/.bashrc   # Linux/Mac
# or restart your terminal
```

**`Permission denied` on npm install**
Never use `sudo npm install -g`. Instead configure a user prefix:
```bash
mkdir ~/.npm-global && npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc && source ~/.bashrc
```

**LinkedIn token expired**
Tokens expire every 60 days. Re-follow Step 3 in `GET_LINKEDIN_TOKEN.md`
and update the `LINKEDIN_ACCESS_TOKEN` secret in GitHub.

**Gemini image not generating**
Check you're using `GEMINI_API_KEY` from **AI Studio** (aistudio.google.com),
not Google Cloud Console — they are different keys.
