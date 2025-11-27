---
description: Verify frontend changes after editing code. Takes screenshot, checks for errors, and reports results.
allowed-tools: Bash(*), Read
model: sonnet
---

# Verify Changes

After making frontend changes, verify they work correctly.

## Instructions

1. **Reload the page** to pick up changes:
   ```bash
   node ~/.claude/plugins/*/skills/website-debug/scripts/browser-eval.js 'location.reload(true)'
   ```

2. **Wait for page load**:
   ```bash
   sleep 2
   ```

3. **Take screenshot**:
   ```bash
   node ~/.claude/plugins/*/skills/website-debug/scripts/browser-screenshot.js
   ```

4. **Check for JavaScript errors**:
   ```bash
   node ~/.claude/plugins/*/skills/website-debug/scripts/browser-console.js --errors
   ```

5. **Analyze and report**:
   - Compare screenshot to expected result
   - List any JavaScript errors
   - Identify if changes applied correctly
   - Note any unexpected side effects

6. **If issues found**:
   - Describe the problem
   - Suggest fixes
   - Offer to make corrections

7. **If successful**:
   - Confirm changes work as expected
   - Ask if any refinements needed

This command is designed for the **edit → verify → iterate** loop that enables self-debugging of frontend work.
