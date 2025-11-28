---
description: Launch interactive element picker for user to select DOM elements. Returns selectors and computed styles.
allowed-tools: Bash(*)
argument-hint: [message to display]
model: sonnet
---

# Pick Element

Launch the interactive element picker so the user can click on DOM elements.

## Instructions

Run the picker with the provided message (or default):

```bash
node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-pick.js "$ARGUMENTS"
```

If no message provided, use: "Select the element you want to debug"

## User Instructions

Tell the user:
- **Click** on any element to select it
- **Cmd/Ctrl + Click** to add more elements to selection
- **Enter** to confirm multi-selection
- **Escape** to cancel

## Output

After the user selects elements, you'll receive:
- CSS selector for each element
- Tag, ID, and classes
- Dimensions and position
- Computed display, visibility, opacity
- Text content preview

Use this information to diagnose issues or write CSS/JS targeting these elements.
