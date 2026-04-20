#!/usr/bin/env bash
# ============================================================
# setup.sh — WSL2 (Ubuntu) Edition
# Run via Claude Code after copying project to ~/
# ============================================================
set -e

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   LinkedIn Cybersec Autopilot — WSL2 Setup       ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ── WSL2 guard ────────────────────────────────────────────
if grep -qi microsoft /proc/version 2>/dev/null; then
  echo "  ✅ Running inside WSL2"
else
  echo "  ⚠️  Not detected as WSL2 — proceed with caution"
fi

# ── Filesystem warning ────────────────────────────────────
if [[ "$PWD" == /mnt/c/* ]]; then
  echo "  ❌ ERROR: Working on /mnt/c/ (Windows filesystem) is slow."
  echo "     Move to Linux home first:"
  echo "     cp -r $PWD ~/ && cd ~/$(basename $PWD) && bash setup.sh"
  exit 1
fi

# ── System packages ────────────────────────────────────────
echo "▶ Installing system packages..."
sudo apt update -qq
sudo apt install -y python3-pip python3-venv git curl -qq
echo "  ✅ System packages ready"

# ── Python venv ───────────────────────────────────────────
[ ! -d "venv" ] && python3 -m venv venv && echo "  ✅ venv created"
source venv/bin/activate
pip install anthropic google-generativeai requests python-dotenv --quiet
echo "  ✅ Python packages installed"

# ── Auto-activate venv on future sessions ─────────────────
ACTIVATE_LINE="source $PWD/venv/bin/activate"
grep -qF "$ACTIVATE_LINE" ~/.bashrc 2>/dev/null || {
  echo "" >> ~/.bashrc
  echo "# Cybersec autopilot venv" >> ~/.bashrc
  echo "$ACTIVATE_LINE" >> ~/.bashrc
  echo "  ✅ Added venv auto-activation to ~/.bashrc"
}

# ── .env template ─────────────────────────────────────────
if [ ! -f .env ]; then
  cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-REPLACE_ME
GEMINI_API_KEY=AIza-REPLACE_ME
LINKEDIN_ACCESS_TOKEN=REPLACE_ME
LINKEDIN_PERSON_URN=urn:li:person:REPLACE_ME
EOF
  echo "  ✅ .env template created — fill in your keys!"
else
  echo "  ℹ️  .env already exists"
fi

# ── .gitignore ────────────────────────────────────────────
[ ! -f .gitignore ] && cat > .gitignore << 'EOF'
.env
venv/
__pycache__/
posts/*/image.png
EOF

mkdir -p posts
for s in scripts/research.py scripts/gen_image.py scripts/publish.py; do
  [ -f "$s" ] && echo "  ✅ $s" || echo "  ❌ MISSING: $s"
done

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Next steps:"
echo "  1. nano .env   (fill in your 4 API keys)"
echo "  2. set -a && source .env && set +a"
echo "  3. python scripts/research.py"
echo "  4. cat posts/\$(date +%Y-%m-%d)/post.json"
echo "  See INSTALL_GUIDE.md for full walkthrough."
echo "═══════════════════════════════════════════════════"
