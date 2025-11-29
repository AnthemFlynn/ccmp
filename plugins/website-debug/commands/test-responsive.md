---
description: Test responsive design across mobile, tablet, and desktop viewports. Takes screenshots at each breakpoint.
allowed-tools: Bash(*)
argument-hint: [url]
model: sonnet
---

# Test Responsive Design

Capture screenshots at multiple viewport sizes to verify responsive design.

## Instructions

1. If URL provided in $ARGUMENTS, navigate first:
   ```bash
   node ~/.claude/plugins/*/skills/website-debug/scripts/browser-nav.js "$ARGUMENTS"
   ```

2. Test **Mobile** (375×667 - iPhone SE):
   ```bash
   node ~/.claude/plugins/*/skills/website-debug/scripts/browser-resize.js --mobile
   node ~/.claude/plugins/*/skills/website-debug/scripts/browser-screenshot.js --output=/tmp/responsive-mobile.png
   ```

3. Test **Tablet** (768×1024 - iPad):
   ```bash
   node ~/.claude/plugins/*/skills/website-debug/scripts/browser-resize.js --tablet
   node ~/.claude/plugins/*/skills/website-debug/scripts/browser-screenshot.js --output=/tmp/responsive-tablet.png
   ```

4. Test **Desktop** (1920×1080):
   ```bash
   node ~/.claude/plugins/*/skills/website-debug/scripts/browser-resize.js --desktop
   node ~/.claude/plugins/*/skills/website-debug/scripts/browser-screenshot.js --output=/tmp/responsive-desktop.png
   ```

5. **Analyze all screenshots** and report:
   - Layout shifts between breakpoints
   - Text overflow or truncation
   - Overlapping elements
   - Hidden/missing content
   - Spacing and alignment issues
   - Navigation usability at each size

Provide specific recommendations for any issues found.
