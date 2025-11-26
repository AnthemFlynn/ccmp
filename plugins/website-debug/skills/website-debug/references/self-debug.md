# Self-Debugging Workflow

Patterns for Claude and AI agents to verify and fix their own frontend work.

## Core Principle

After making any frontend change, verify it worked:
1. **Screenshot** - Visual verification
2. **Console** - Check for errors
3. **DOM** - Confirm structure
4. **Iterate** - Fix issues and repeat

## Basic Verification Loop

```bash
# After modifying HTML/CSS/JS files:

# 1. Reload the page (if not using hot reload)
./browser-nav.js http://localhost:3000

# 2. Take screenshot to verify visual result
./browser-screenshot.js

# 3. Check for any JavaScript errors
./browser-console.js --errors

# 4. If issues found, fix and repeat
```

## Structured Debugging Protocol

### Phase 1: Initial Assessment
```bash
# Get page summary
./browser-dom.js

# Take baseline screenshot
./browser-screenshot.js --output=/tmp/current-state.png

# Capture any errors
./browser-console.js --errors > /tmp/errors.txt
```

### Phase 2: Make Changes
After editing source files:
```bash
# Force reload (bypass cache)
./browser-eval.js 'location.reload(true)'

# Wait for page load
sleep 2

# Take new screenshot
./browser-screenshot.js --output=/tmp/after-change.png
```

### Phase 3: Verify
```bash
# Check for new errors
./browser-console.js --errors

# Verify element exists (example: new button)
./browser-eval.js 'document.querySelector(".new-button") ? "Found" : "Missing"'

# Verify styling applied
./browser-eval.js 'getComputedStyle(document.querySelector(".new-button")).backgroundColor'
```

### Phase 4: Iterate
If issues found:
1. Identify the problem from screenshot/console
2. Fix the source code
3. Return to Phase 2

## Common Self-Fix Patterns

### CSS Not Applying

**Symptom**: Element exists but looks wrong
**Diagnosis**:
```bash
# Check if styles computed correctly
./browser-eval.js 'getComputedStyle(document.querySelector(".my-element")).cssText.slice(0, 500)'

# Check for conflicting selectors
./browser-eval.js '(() => {
  const el = document.querySelector(".my-element");
  const sheets = [...document.styleSheets];
  const matches = [];
  sheets.forEach(sheet => {
    try {
      [...sheet.cssRules].forEach(rule => {
        if (el.matches(rule.selectorText)) matches.push(rule.selectorText);
      });
    } catch {}
  });
  return matches;
})()'
```

**Fixes to try**:
1. Increase specificity
2. Check for `!important` overrides
3. Verify selector matches element

### Element Not Visible

**Symptom**: DOM shows element but not visible
**Diagnosis**:
```bash
./browser-eval.js '(() => {
  const el = document.querySelector(".my-element");
  const s = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  return {
    exists: !!el,
    display: s.display,
    visibility: s.visibility,
    opacity: s.opacity,
    width: r.width,
    height: r.height,
    inViewport: r.top < window.innerHeight && r.bottom > 0
  };
})()'
```

**Fixes based on result**:
- `display: none` → Check CSS rules hiding it
- `width/height: 0` → Add dimensions or content
- `opacity: 0` → Check for fade animations
- Not in viewport → Check positioning/scroll

### JavaScript Not Running

**Symptom**: Interactive features don't work
**Diagnosis**:
```bash
# Check for errors
./browser-console.js --errors

# Check if script loaded
./browser-eval.js 'document.querySelectorAll("script").length'

# Check if function exists
./browser-eval.js 'typeof myFunction'
```

**Fixes based on result**:
- Syntax error → Fix the JavaScript
- Script not loaded → Check path/build process
- Function undefined → Check load order, exports

### Layout Broken

**Symptom**: Elements positioned incorrectly
**Diagnosis**:
```bash
# Take screenshot
./browser-screenshot.js

# Check flex/grid container
./browser-eval.js '(() => {
  const container = document.querySelector(".container");
  const s = getComputedStyle(container);
  return { display: s.display, flexDirection: s.flexDirection, gridTemplateColumns: s.gridTemplateColumns };
})()'
```

**Common fixes**:
- Missing `display: flex/grid` on container
- Wrong `flex-direction`
- Missing `width` on flex children
- Grid columns not matching children

## Responsive Verification

### Test All Breakpoints
```bash
# Mobile
./browser-resize.js --mobile
./browser-screenshot.js --output=/tmp/mobile.png
./browser-console.js --errors

# Tablet  
./browser-resize.js --tablet
./browser-screenshot.js --output=/tmp/tablet.png

# Desktop
./browser-resize.js --desktop
./browser-screenshot.js --output=/tmp/desktop.png
```

### Compare Screenshots
After each breakpoint, Claude should analyze the screenshot for:
- Layout shifts
- Overlapping elements
- Text overflow
- Hidden/missing elements
- Incorrect spacing

## Interactive Feature Testing

### Form Validation
```bash
# Fill form with test data
./browser-eval.js 'document.querySelector("#email").value = "test@example.com"'
./browser-eval.js 'document.querySelector("#password").value = "test123"'

# Submit and check result
./browser-eval.js 'document.querySelector("form").submit()'
./browser-screenshot.js
./browser-console.js --errors
```

### Click/Hover States
```bash
# Test button click
./browser-eval.js 'document.querySelector(".button").click()'
./browser-screenshot.js

# Check state changed
./browser-eval.js 'document.querySelector(".modal")?.style.display'
```

## Automated Verification Script

For repeated checks, use this pattern:
```bash
#!/bin/bash
# verify-page.sh - Run after changes

URL="${1:-http://localhost:3000}"
OUT_DIR="/tmp/debug-$(date +%s)"
mkdir -p "$OUT_DIR"

echo "Verifying $URL..."

# Navigate
./browser-nav.js "$URL"
sleep 2

# Screenshot
./browser-screenshot.js --output="$OUT_DIR/screenshot.png"
echo "Screenshot: $OUT_DIR/screenshot.png"

# Errors
./browser-console.js --errors > "$OUT_DIR/errors.txt"
if [ -s "$OUT_DIR/errors.txt" ]; then
  echo "⚠️  Errors found:"
  cat "$OUT_DIR/errors.txt"
else
  echo "✓ No JavaScript errors"
fi

# DOM summary
./browser-dom.js > "$OUT_DIR/dom.txt"
echo "DOM summary saved"

echo "Done. Files in $OUT_DIR"
```

## Error Recovery Strategies

### When Screenshot Shows Blank Page
1. Check console for critical errors
2. Verify server is running
3. Check network requests (404, 500)
4. Verify correct URL

### When Console Shows Many Errors
1. Fix first error (often causes cascade)
2. Reload and recheck
3. Address errors in order

### When Element Is "Almost Right"
1. Use picker to select element: `./browser-pick.js "Select the problematic element"`
2. Get full computed styles
3. Compare to expected values
4. Adjust CSS incrementally

## Best Practices

1. **Always screenshot after changes** - Visual verification catches most issues
2. **Check console immediately** - Catch JS errors early
3. **Test responsive early** - Layout issues compound
4. **Verify one change at a time** - Easier to identify what broke
5. **Save debug output** - Reference for comparison
6. **Use the picker for precision** - Get exact selectors from user
