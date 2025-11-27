---
description: Navigate the browser to a URL. Use --new to open in new tab.
allowed-tools: Bash(*)
argument-hint: <url> [--new]
model: haiku
---

# Navigate

Navigate the browser to a URL.

```bash
node ~/.claude/plugins/*/skills/website-debug/scripts/browser-nav.js $ARGUMENTS
```

## Options

- `<url>`: Navigate current tab to URL
- `<url> --new`: Open URL in new tab

If URL doesn't include protocol, `https://` is assumed.

Confirm successful navigation with page title.
