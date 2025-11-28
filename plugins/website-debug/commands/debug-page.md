---
description: Start a debugging session for a webpage. Launches browser, takes screenshot, and checks for errors.
allowed-tools: Bash(*), Read, Write
argument-hint: [url]
model: sonnet
---

# Debug Page

Start a comprehensive debugging session for a webpage.

## Instructions

1. **Start browser** (if not already running):
   ```bash
   node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-start.js
   ```

2. **Navigate to URL** (use $ARGUMENTS if provided, otherwise ask):
   ```bash
   node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-nav.js "$ARGUMENTS"
   ```

3. **Take initial screenshot**:
   ```bash
   node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-screenshot.js
   ```

4. **Check for JavaScript errors**:
   ```bash
   node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-console.js --errors
   ```

5. **Get page summary**:
   ```bash
   node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-dom.js
   ```

6. **Analyze the screenshot** visually and report:
   - Any visible layout issues
   - Console errors found
   - DOM structure overview
   - Recommendations for what to investigate

If $ARGUMENTS is empty, ask the user for the URL to debug.

After completing the initial assessment, ask the user what specific issue they'd like to investigate or if they want to use the element picker to select a problematic element.
