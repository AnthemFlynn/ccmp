---
description: Diagnose and fix CSS issues for a specific element. Uses the css-debugger agent for expert analysis.
allowed-tools: Bash(*), Read, Write
argument-hint: <selector> [issue description]
model: sonnet
---

# Fix CSS

Diagnose and fix CSS issues for a specific element.

## Instructions

Use the **css-debugger agent** for this task.

1. **Identify the element**: Use $ARGUMENTS to get the selector
   - If no selector provided, run `/pick-element` first

2. **Gather information**:
   ```bash
   node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-eval.js '(() => {
     const el = document.querySelector("SELECTOR");
     if (!el) return "Element not found";
     const s = getComputedStyle(el);
     return {
       display: s.display,
       visibility: s.visibility,
       opacity: s.opacity,
       width: s.width,
       height: s.height,
       position: s.position,
       top: s.top,
       left: s.left,
       zIndex: s.zIndex,
       margin: s.margin,
       padding: s.padding,
       flexDirection: s.flexDirection,
       justifyContent: s.justifyContent,
       alignItems: s.alignItems,
       overflow: s.overflow,
       transform: s.transform
     };
   })()'
   ```

3. **Take screenshot** to see current state:
   ```bash
   node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-screenshot.js
   ```

4. **Analyze the issue** based on:
   - Computed styles
   - Visual appearance
   - User's description (if provided)

5. **Propose fix** with specific CSS changes

6. **After making changes**, use `/verify-changes` to confirm fix worked

Delegate the actual analysis and fix proposal to the css-debugger agent for expert-level diagnosis.
