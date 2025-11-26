---
description: Analyze page performance - load times, DOM size, memory, and large resources.
allowed-tools: Bash(*)
model: sonnet
---

# Performance Analysis

Run a comprehensive performance analysis on the current page.

Use the **performance-debugger agent** for this task.

## Collect Metrics

1. **Page Load Timing**:
   ```bash
   node ~/.claude/plugins/*/skills/website-debug/scripts/browser-eval.js '(() => {
     const t = performance.timing;
     return {
       firstByte: t.responseStart - t.navigationStart,
       domInteractive: t.domInteractive - t.navigationStart,
       domContentLoaded: t.domContentLoadedEventEnd - t.navigationStart,
       loadComplete: t.loadEventEnd - t.navigationStart
     };
   })()'
   ```

2. **DOM Analysis**:
   ```bash
   node ~/.claude/plugins/*/skills/website-debug/scripts/browser-eval.js '(() => {
     const all = document.querySelectorAll("*");
     return {
       totalElements: all.length,
       scripts: document.scripts.length,
       stylesheets: document.styleSheets.length,
       images: document.images.length
     };
   })()'
   ```

3. **Large Resources**:
   ```bash
   node ~/.claude/plugins/*/skills/website-debug/scripts/browser-eval.js 'performance.getEntriesByType("resource").filter(r => r.transferSize > 50000).map(r => ({ name: r.name.split("/").pop(), kb: (r.transferSize/1024).toFixed(1) })).slice(0,10)'
   ```

4. **Screenshot** for context:
   ```bash
   node ~/.claude/plugins/*/skills/website-debug/scripts/browser-screenshot.js
   ```

## Report

Provide a summary with:
- Load time assessment (good/needs improvement/poor)
- DOM size assessment
- Largest resources
- Top 3 recommendations for improvement
