---
description: Close the browser session gracefully. Use --force to kill all Chrome processes.
allowed-tools: Bash(*)
argument-hint: [--force]
model: haiku
---

# Close Browser

Close the browser debugging session.

```bash
node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-close.js $ARGUMENTS
```

## Options

- No arguments: Graceful close via Puppeteer
- `--force`: Kill all Chrome processes (useful if stuck)

Confirm when browser is closed.
