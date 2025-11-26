---
description: Execute JavaScript in the browser's page context. Great for inspecting DOM, computed styles, or testing fixes.
allowed-tools: Bash(*)
argument-hint: <javascript expression>
model: haiku
---

# Evaluate JavaScript

Execute JavaScript in the active browser tab's page context.

```bash
node ~/.claude/plugins/*/skills/website-debug/scripts/browser-eval.js '$ARGUMENTS'
```

## Common Uses

**Get element info:**
```
document.querySelector(".selector")
```

**Check computed styles:**
```
getComputedStyle(document.querySelector(".btn")).backgroundColor
```

**Count elements:**
```
document.querySelectorAll("a").length
```

**Get bounding rect:**
```
document.querySelector(".header").getBoundingClientRect()
```

Return the result to the user and explain what it means in context.
