#!/bin/bash

# Swiggy Telegram Bot - GitHub & Railway Setup Script
# This script initializes git repo and prepares for Railway deployment

set -e

echo "=================================="
echo "Swiggy Telegram Bot Setup"
echo "=================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git not installed. Install git and try again."
    exit 1
fi

# Initialize git repo
if [ ! -d ".git" ]; then
    echo "[1/5] Initializing Git repository..."
    git init
    git config user.email "bot@example.com"
    git config user.name "Swiggy Bot"
else
    echo "[1/5] Git repository already initialized"
fi

# Add all files
echo "[2/5] Adding files to git..."
git add .

# Create initial commit
echo "[3/5] Creating initial commit..."
git commit -m "Initial: Swiggy Telegram Bot - Firebase URLs, Link Manager, Admin Auth, Railway Ready" 2>/dev/null || echo "Files already committed"

# Display next steps
echo "[4/5] Setup complete!"
echo ""
echo "=================================="
echo "📋 GITHUB SETUP"
echo "=================================="
echo ""
echo "1. Go to https://github.com/new"
echo "2. Create repository 'swiggy-telegram-bot'"
echo "3. Copy the repository URL"
echo "4. Run this command:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/swiggy-telegram-bot.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "=================================="
echo "🚀 RAILWAY DEPLOYMENT"
echo "=================================="
echo ""
echo "1. Go to https://railway.app"
echo "2. Click 'New Project'"
echo "3. Select 'Deploy from GitHub'"
echo "4. Authorize Railway to access GitHub"
echo "5. Select 'swiggy-telegram-bot' repository"
echo "6. Click 'Deploy'"
echo ""
echo "=================================="
echo "⚙️ ENVIRONMENT VARIABLES (on Railway)"
echo "=================================="
echo ""
echo "Add these variables in Railway Dashboard → Variables:"
echo ""
echo "  TELEGRAM_TOKEN        = your_bot_token"
echo "  ADMIN_IDS             = 123456789,987654321"
echo "  FIREBASE_URL          = https://your-project.firebaseio.com"
echo ""
echo "=================================="
echo "✅ LOCAL TESTING"
echo "=================================="
echo ""
echo "Before pushing to GitHub:"
echo ""
echo "  1. pip install -r requirements.txt"
echo "  2. cp .env.example .env"
echo "  3. Edit .env with your credentials"
echo "  4. python bot.py"
echo ""
echo "=================================="
echo "📝 NEXT STEPS"
echo "=================================="
echo ""
echo "1. Edit .env with your credentials"
echo "2. Test bot locally: python bot.py"
echo "3. Push to GitHub"
echo "4. Deploy on Railway"
echo "5. Monitor logs: railway logs"
echo ""
echo "[5/5] Done! 🎉"
