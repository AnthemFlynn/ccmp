---
description: Inspect DOM structure. Get page summary, element HTML, or tree visualization.
allowed-tools: Bash(*)
argument-hint: [selector | --tree]
model: haiku
---

# DOM Inspection

Inspect the page's DOM structure.

```bash
node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-dom.js $ARGUMENTS
```

## Usage

- No arguments: Page summary (element counts, headings, structure)
- `selector`: Get element's outerHTML
- `selector --inner`: Get element's innerHTML  
- `--tree`: Visual DOM tree (3 levels deep)
- `--tree --depth=5`: Custom depth

## Examples

```bash
# Page overview
/dom

# Get specific element
/dom ".header"

# DOM tree visualization
/dom --tree
```
