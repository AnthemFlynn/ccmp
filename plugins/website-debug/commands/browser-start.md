---
description: Start Chrome or WebKit browser with debugging enabled. Use --profile to preserve logins, --webkit for Safari testing.
allowed-tools: Bash(*)
argument-hint: [--profile | --webkit | --headless]
model: haiku
---

# Start Browser

Launch a browser session with remote debugging enabled.

```bash
node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-start.js $ARGUMENTS
```

## Options

- No arguments: Fresh Chrome profile
- `--profile`: Chrome with your profile (preserves logins, cookies)
- `--webkit`: Playwright WebKit (Safari-like behavior)
- `--headless`: Run without visible window

After starting, confirm the browser is ready and suggest next steps (navigate to a URL).
