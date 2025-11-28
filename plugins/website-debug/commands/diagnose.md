---
description: Run comprehensive diagnostics on an element or the entire page. Checks CSS, JS errors, accessibility, and more.
allowed-tools: Bash(*)
argument-hint: [selector]
model: opus
---

# Diagnose

Run comprehensive diagnostics on a specific element or the entire page.

## If selector provided ($ARGUMENTS):

1. **Check element exists**:
   ```bash
   node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-eval.js 'document.querySelector("$ARGUMENTS") !== null'
   ```

2. **Get element details**:
   ```bash
   node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-eval.js '(() => {
     const el = document.querySelector("$ARGUMENTS");
     if (!el) return "Element not found";
     const s = getComputedStyle(el);
     const r = el.getBoundingClientRect();
     return {
       tag: el.tagName,
       id: el.id,
       classes: [...el.classList],
       dimensions: { width: r.width, height: r.height },
       position: { top: r.top, left: r.left },
       styles: {
         display: s.display,
         visibility: s.visibility,
         opacity: s.opacity,
         position: s.position,
         zIndex: s.zIndex,
         overflow: s.overflow,
         flex: s.display === "flex" ? { direction: s.flexDirection, justify: s.justifyContent, align: s.alignItems } : null,
         grid: s.display === "grid" ? { columns: s.gridTemplateColumns, rows: s.gridTemplateRows } : null
       },
       text: el.textContent?.slice(0, 100)
     };
   })()'
   ```

3. **Screenshot element**:
   ```bash
   node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-screenshot.js --selector="$ARGUMENTS"
   ```

## If no selector (full page diagnosis):

1. **Take screenshot**:
   ```bash
   node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-screenshot.js
   ```

2. **Check for JavaScript errors**:
   ```bash
   node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-console.js --errors
   ```

3. **Check network failures**:
   ```bash
   node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-network.js --failures
   ```

4. **Get page summary**:
   ```bash
   node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-dom.js
   ```

5. **Check accessibility basics**:
   ```bash
   node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-eval.js '(() => {
     const issues = [];
     // Images without alt
     const imgs = document.querySelectorAll("img:not([alt])");
     if (imgs.length) issues.push(`${imgs.length} images missing alt text`);
     // Buttons/links without text
     const emptyBtns = [...document.querySelectorAll("button, a")].filter(el => !el.textContent.trim() && !el.getAttribute("aria-label"));
     if (emptyBtns.length) issues.push(`${emptyBtns.length} buttons/links without accessible text`);
     // Form inputs without labels
     const inputs = document.querySelectorAll("input:not([type=hidden]):not([type=submit])");
     const unlabeled = [...inputs].filter(i => !i.getAttribute("aria-label") && !document.querySelector(`label[for="${i.id}"]`));
     if (unlabeled.length) issues.push(`${unlabeled.length} form inputs without labels`);
     return issues.length ? issues : "No basic accessibility issues found";
   })()'
   ```

## Report Format

Provide a structured diagnosis:

### Visual Analysis
- What the screenshot shows
- Any obvious layout issues

### JavaScript Errors
- List errors found (or confirm none)
- Suggest fixes for each

### Network Issues  
- Failed requests (or confirm none)
- Suggest causes

### Accessibility
- Issues found
- Recommendations

### Recommendations
- Priority fixes
- Suggestions for improvement
