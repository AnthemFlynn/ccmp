---
description: Watch network requests in real-time. Great for debugging API calls.
allowed-tools: Bash(*)
argument-hint: [--failures | --xhr]
model: haiku
---

# Watch Network

Monitor network requests in real-time.

```bash
node ~/.claude/plugins/*/skills/website-debug/scripts/browser-network.js --watch $ARGUMENTS
```

## Options

- No arguments: All network requests
- `--failures`: Only 4xx/5xx errors
- `--xhr`: Only XHR/fetch (API calls)

Press Ctrl+C to stop watching.

Report any failed requests and suggest potential causes.
