---
description: Take a screenshot of the current browser viewport. Use --full for full page, --selector for specific element.
allowed-tools: Bash(*)
argument-hint: [--full | --selector=".class"]
model: haiku
---

# Screenshot

Take a screenshot of the current browser state.

```bash
node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-screenshot.js $ARGUMENTS
```

## Options

- No arguments: Viewport screenshot
- `--full`: Full page screenshot (scrollable content)
- `--selector=".class"`: Screenshot of specific element

After capturing, analyze the screenshot for any visual issues.
