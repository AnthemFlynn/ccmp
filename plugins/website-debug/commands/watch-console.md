---
description: Watch browser console in real-time. Shows errors, warnings, and logs as they happen.
allowed-tools: Bash(*)
argument-hint: [--errors | --warnings]
model: haiku
---

# Watch Console

Monitor browser console output in real-time.

```bash
node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-console.js --watch $ARGUMENTS
```

## Options

- No arguments: All console messages
- `--errors`: Only error messages
- `--warnings`: Errors and warnings

Press Ctrl+C to stop watching.

Report any errors that appear and suggest fixes.
