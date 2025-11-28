#!/bin/bash
#
# install.sh - Install the website-debug plugin for Claude Code
#

set -e

echo "Installing website-debug plugin..."
echo ""

# Detect plugin directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$SCRIPT_DIR/skills/website-debug"

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ first."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js 18+ required. Found: $(node -v)"
    exit 1
fi
echo "✓ Node.js $(node -v)"

# Install Node.js dependencies in skill directory
echo ""
echo "Installing dependencies..."
cd "$SKILL_DIR"

# Try local install first, fall back to global
if npm install 2>/dev/null; then
    echo "✓ Dependencies installed locally"
else
    echo "Local install failed, trying global puppeteer-core..."
    npm install -g puppeteer-core 2>/dev/null || {
        echo "❌ Failed to install puppeteer-core"
        echo "   Try manually: npm install -g puppeteer-core"
        exit 1
    }
    echo "✓ puppeteer-core installed globally"
fi

# Create cache directory for browser profiles
mkdir -p ~/.cache/website-debug
echo "✓ Cache directory created"

# Make scripts executable
chmod +x "$SKILL_DIR/scripts/"*.js 2>/dev/null || true
echo "✓ Scripts made executable"

# Optional: Install Playwright for WebKit
echo ""
read -p "Install Playwright for Safari/WebKit support? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing Playwright..."
    npm install -g playwright 2>/dev/null && npx playwright install webkit 2>/dev/null && {
        echo "✓ Playwright + WebKit installed"
    } || {
        echo "⚠️  Playwright installation failed (Chrome debugging will still work)"
    }
else
    echo "⏭️  Skipping Playwright (Chrome debugging will still work)"
fi

echo ""
echo "=========================================="
echo "✅ website-debug plugin installed!"
echo ""
echo "Usage:"
echo "  /debug-page <url>     - Start debugging session"
echo "  /screenshot           - Take screenshot"
echo "  /pick-element         - Interactive element picker"
echo "  /test-responsive      - Test responsive design"
echo "  /verify-changes       - Verify after code changes"
echo "  /browser-start        - Start browser"
echo "  /browser-eval <js>    - Execute JavaScript"
echo ""
echo "Subagents (auto-invoked):"
echo "  css-debugger          - CSS/layout issues"
echo "  js-debugger           - JavaScript errors"
echo "  responsive-tester     - Viewport testing"
echo "  visual-verifier       - Self-debugging loop"
echo "  network-debugger      - API/request issues"
echo "=========================================="
