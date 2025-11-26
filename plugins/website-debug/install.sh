#!/bin/bash
#
# install.sh - Install the website-debug plugin for Claude Code
#

set -e

echo "Installing website-debug plugin..."
echo ""

# Detect plugin directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_NAME="website-debug"

# Install Node.js dependencies
echo "Installing dependencies..."
cd "$SCRIPT_DIR/skills/website-debug"
npm install 2>/dev/null || {
    echo "Installing puppeteer-core globally..."
    npm install -g puppeteer-core
}

# Optional: Install Playwright for WebKit
echo ""
echo "Installing Playwright for Safari/WebKit support (optional)..."
npm install -g playwright 2>/dev/null && npx playwright install webkit 2>/dev/null || {
    echo "⚠️  Playwright installation skipped (Chrome debugging will still work)"
}

# Make scripts executable
chmod +x "$SCRIPT_DIR/skills/website-debug/scripts/"*.js 2>/dev/null || true

echo ""
echo "=========================================="
echo "✓ website-debug plugin installed!"
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
