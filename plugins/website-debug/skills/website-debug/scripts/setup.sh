#!/bin/bash
#
# setup.sh - Install dependencies for website-debug skill
#

set -e

echo "Setting up website-debug skill..."
echo ""

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS_DIR="$SKILL_DIR/scripts"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js first:"
    echo "   https://nodejs.org/ or: brew install node"
    exit 1
fi
echo "✓ Node.js $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm."
    exit 1
fi
echo "✓ npm $(npm --version)"

# Install puppeteer-core globally
echo ""
echo "Installing puppeteer-core..."
npm install -g puppeteer-core 2>/dev/null || npm install puppeteer-core --save 2>/dev/null
echo "✓ puppeteer-core installed"

# Optional: Install Playwright for WebKit support
echo ""
echo "Installing Playwright for Safari/WebKit support (optional)..."
if npm install -g playwright 2>/dev/null; then
    npx playwright install webkit 2>/dev/null || true
    echo "✓ Playwright + WebKit installed"
else
    echo "⚠ Playwright installation skipped (Chrome debugging will still work)"
fi

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x "$SCRIPTS_DIR"/*.js 2>/dev/null || true
echo "✓ Scripts are executable"

# Create cache directory
mkdir -p ~/.cache/website-debug
echo "✓ Cache directory ready"

# Check Chrome
echo ""
if [[ "$OSTYPE" == "darwin"* ]]; then
    CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if [ -f "$CHROME_PATH" ]; then
        echo "✓ Chrome found at $CHROME_PATH"
    else
        echo "⚠ Chrome not found. Install from: https://www.google.com/chrome/"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v google-chrome &> /dev/null; then
        echo "✓ Chrome found"
    else
        echo "⚠ Chrome not found. Install with: sudo apt install google-chrome-stable"
    fi
fi

echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo ""
echo "Quick start:"
echo "  cd $SCRIPTS_DIR"
echo "  ./browser-start.js            # Start Chrome"
echo "  ./browser-nav.js http://localhost:3000"
echo "  ./browser-screenshot.js       # Take screenshot"
echo ""
echo "Or use with Claude Code:"
echo "  Ask Claude to 'debug this page' or 'check my site'"
echo "=========================================="
