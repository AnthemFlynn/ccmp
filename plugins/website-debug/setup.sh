#!/bin/bash
#
# setup.sh - Set up dependencies for website-debug plugin
#

set -e

echo "🔧 Setting up website-debug plugin dependencies..."
echo ""

# Check Node.js
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

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found"
    exit 1
fi
echo "✓ npm $(npm -v)"

# Install puppeteer-core
echo ""
echo "Installing puppeteer-core..."
npm install -g puppeteer-core || {
    echo "⚠️  Global install failed, trying local..."
    npm install puppeteer-core
}
echo "✓ puppeteer-core installed"

# Check for Chrome
echo ""
echo "Checking for Chrome..."
CHROME_PATHS=(
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    "/usr/bin/google-chrome"
    "/usr/bin/google-chrome-stable"
    "/usr/bin/chromium"
    "/usr/bin/chromium-browser"
)

CHROME_FOUND=false
for CHROME_PATH in "${CHROME_PATHS[@]}"; do
    if [ -f "$CHROME_PATH" ]; then
        echo "✓ Chrome found: $CHROME_PATH"
        CHROME_FOUND=true
        break
    fi
done

if [ "$CHROME_FOUND" = false ]; then
    echo "⚠️  Chrome not found in standard locations"
    echo "   Please ensure Chrome is installed for browser debugging"
fi

# Optional: Playwright for WebKit
echo ""
read -p "Install Playwright for Safari/WebKit support? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing Playwright..."
    npm install -g playwright
    npx playwright install webkit
    echo "✓ Playwright + WebKit installed"
else
    echo "⏭️  Skipping Playwright (Chrome debugging will still work)"
fi

# Create cache directory
mkdir -p ~/.cache/website-debug
echo "✓ Cache directory created"

# Make scripts executable
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$SCRIPT_DIR/skills/website-debug/scripts/"*.js 2>/dev/null || true
echo "✓ Scripts made executable"

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "Quick start:"
echo "  /browser-start      - Launch browser"
echo "  /debug-page <url>   - Start debugging"
echo "=========================================="
