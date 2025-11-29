---
name: website-debug
description: >
  Frontend website debugging toolkit using Chrome DevTools Protocol with Playwright/WebKit fallbacks.
  Use this skill when: (1) Debugging CSS, HTML, or JavaScript issues on a webpage, (2) Taking screenshots
  to verify visual changes, (3) Inspecting DOM structure or console errors, (4) Testing responsive layouts,
  (5) Extracting selectors for automation, (6) Self-debugging frontend work Claude has created,
  (7) User says "debug this page", "check my site", "why doesn't this look right", or "fix the frontend".
  Supports Chrome (primary) and Safari/WebKit (via Playwright). Designed for agent-driven debugging loops.
---

# Website Debugging Skill

Lightweight, token-efficient browser debugging toolkit for frontend development. Uses CLI scripts instead of MCP servers to minimize context usage (~300 tokens vs 13k-18k).

## Quick Start

Use the slash commands for easiest access:
- `/debug-page <url>` - Start debugging session
- `/screenshot` - Take screenshot
- `/pick-element` - Interactive element selection
- `/test-responsive` - Test at all breakpoints
- `/verify-changes` - Verify after making changes

### Or use scripts directly:

```bash
# Start browser
node scripts/browser-start.js
node scripts/browser-start.js --profile  # Preserve logins
node scripts/browser-start.js --webkit   # Safari/WebKit

# Navigate
node scripts/browser-nav.js https://localhost:3000

# Debug
node scripts/browser-screenshot.js
node scripts/browser-eval.js 'document.title'
node scripts/browser-pick.js "Select element"
node scripts/browser-console.js --errors
node scripts/browser-network.js --failures
```

## Core Tools Reference

| Script | Purpose | Output |
|--------|---------|--------|
| `browser-start.sh` | Launch Chrome/WebKit with debug port | Status message |
| `browser-nav.sh <url>` | Navigate to URL | Confirmation |
| `browser-screenshot.sh` | Capture viewport | File path (PNG) |
| `browser-eval.sh '<js>'` | Run JS in page | Result or error |
| `browser-pick.sh "<msg>"` | Interactive selector | CSS selectors |
| `browser-console.sh` | Get console output | Logs/errors |
| `browser-network.sh` | Network activity | Request/response data |
| `browser-dom.sh "<sel>"` | Get DOM snapshot | HTML fragment |
| `browser-close.sh` | Close browser | Confirmation |

## Self-Debugging Workflow

When debugging frontend code Claude has written or modified:

### 1. Visual Verification Loop
```bash
# After making CSS/HTML changes, verify visually
./scripts/browser-screenshot.sh
# Claude reads the screenshot, identifies issues, iterates
```

### 2. Console Error Detection
```bash
# Check for JavaScript errors after changes
./scripts/browser-console.sh --errors
# Fix any errors found, re-verify
```

### 3. Responsive Testing
```bash
# Test at different viewport sizes
./scripts/browser-resize.sh 375 667   # iPhone SE
./scripts/browser-screenshot.sh
./scripts/browser-resize.sh 768 1024  # iPad
./scripts/browser-screenshot.sh
./scripts/browser-resize.sh 1920 1080 # Desktop
./scripts/browser-screenshot.sh
```

### 4. Element Inspection
```bash
# When user reports "X looks wrong", have them select it
./scripts/browser-pick.sh "Click on the element that looks wrong"
# Returns detailed info including computed styles
```

## Browser Engine Selection

### Chrome (Default)
Primary engine. Uses Chrome DevTools Protocol on port 9222.
- Best debugging experience
- Full DevTools compatibility  
- Use `--profile` to preserve logins

### WebKit/Safari
Fallback via Playwright's WebKit build. Closest to Safari behavior on macOS.
```bash
./scripts/browser-start.sh --webkit
```
- Use for Safari-specific testing
- Layout verification
- WebKit-specific bugs

### When to Use Each

| Scenario | Engine |
|----------|--------|
| General debugging | Chrome |
| Safari layout issues | WebKit |
| Testing with logins | Chrome `--profile` |
| Cross-browser comparison | Both |
| CI/headless testing | Chrome or WebKit |

## Advanced Usage

### Detailed Documentation
For complex scenarios, load the appropriate reference:

- **CSS Debugging**: See [references/css-debug.md](references/css-debug.md)
- **JavaScript Errors**: See [references/js-debug.md](references/js-debug.md)
- **Network Issues**: See [references/network-debug.md](references/network-debug.md)
- **Responsive Design**: See [references/responsive-debug.md](references/responsive-debug.md)
- **Performance**: See [references/performance-debug.md](references/performance-debug.md)

### Composable Output

All scripts output to files when practical, enabling:
```bash
# Capture multiple screenshots for comparison
./scripts/browser-screenshot.sh > /tmp/before.png
# ... make changes ...
./scripts/browser-screenshot.sh > /tmp/after.png

# Save DOM snapshot for analysis
./scripts/browser-dom.sh "body" > /tmp/page-structure.html

# Export console log for review
./scripts/browser-console.sh > /tmp/console-log.txt
```

### Chaining Commands
```bash
# Navigate and screenshot in one command
./scripts/browser-nav.sh https://example.com && ./scripts/browser-screenshot.sh

# Full page audit
./scripts/browser-nav.sh $URL && \
  ./scripts/browser-console.sh --errors > /tmp/errors.txt && \
  ./scripts/browser-screenshot.sh
```

## Setup Requirements

### Chrome
Chrome must be launchable from command line. The start script handles this automatically.

### WebKit (Optional)
For Safari testing, ensure Playwright is installed:
```bash
npm install -g playwright
npx playwright install webkit
```

### Dependencies
Scripts require Node.js and puppeteer-core:
```bash
npm install -g puppeteer-core
```

## Troubleshooting

### "Cannot connect to browser"
Browser may not be running or wrong port:
```bash
./scripts/browser-start.sh  # Restart browser
```

### "Permission denied"
Scripts may need execute permission:
```bash
chmod +x ./scripts/*.sh
```

### Chrome already running
Kill existing instances first:
```bash
killall "Google Chrome" 2>/dev/null
./scripts/browser-start.sh
```

### WebKit not found
Install Playwright browsers:
```bash
npx playwright install webkit
```
