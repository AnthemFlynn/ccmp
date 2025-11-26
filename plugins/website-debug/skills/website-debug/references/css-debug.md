# CSS Debugging Reference

Advanced CSS debugging workflows and patterns for frontend development.

## Quick Diagnostics

### Check Element Visibility
```bash
# Is element visible?
./browser-eval.js '(() => {
  const el = document.querySelector(".target");
  const s = getComputedStyle(el);
  return {
    display: s.display,
    visibility: s.visibility,
    opacity: s.opacity,
    hidden: el.hidden,
    height: s.height,
    width: s.width,
    overflow: s.overflow
  };
})()'
```

### Element Not Showing?
Common causes and checks:

```bash
# Check display property
./browser-eval.js 'getComputedStyle(document.querySelector(".target")).display'
# If "none" - element is hidden by CSS

# Check visibility
./browser-eval.js 'getComputedStyle(document.querySelector(".target")).visibility'
# If "hidden" - element takes space but invisible

# Check opacity
./browser-eval.js 'getComputedStyle(document.querySelector(".target")).opacity'
# If "0" - element is transparent

# Check dimensions
./browser-eval.js 'document.querySelector(".target").getBoundingClientRect()'
# If width/height is 0 - element has no size

# Check if off-screen
./browser-eval.js '(() => {
  const r = document.querySelector(".target").getBoundingClientRect();
  return {
    inViewport: r.top >= 0 && r.left >= 0 && r.bottom <= window.innerHeight && r.right <= window.innerWidth,
    position: { top: r.top, left: r.left }
  };
})()'
```

## Layout Issues

### Flexbox Debugging
```bash
# Check flex container
./browser-eval.js '(() => {
  const el = document.querySelector(".flex-container");
  const s = getComputedStyle(el);
  return {
    display: s.display,
    flexDirection: s.flexDirection,
    justifyContent: s.justifyContent,
    alignItems: s.alignItems,
    flexWrap: s.flexWrap,
    gap: s.gap
  };
})()'

# Check flex items
./browser-eval.js '[...document.querySelectorAll(".flex-container > *")].map(el => {
  const s = getComputedStyle(el);
  return {
    flexGrow: s.flexGrow,
    flexShrink: s.flexShrink,
    flexBasis: s.flexBasis,
    alignSelf: s.alignSelf
  };
})'
```

### Grid Debugging
```bash
# Check grid container
./browser-eval.js '(() => {
  const el = document.querySelector(".grid-container");
  const s = getComputedStyle(el);
  return {
    display: s.display,
    gridTemplateColumns: s.gridTemplateColumns,
    gridTemplateRows: s.gridTemplateRows,
    gap: s.gap,
    gridAutoFlow: s.gridAutoFlow
  };
})()'
```

### Box Model
```bash
# Full box model breakdown
./browser-eval.js '(() => {
  const el = document.querySelector(".target");
  const s = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  return {
    content: { width: r.width, height: r.height },
    padding: { top: s.paddingTop, right: s.paddingRight, bottom: s.paddingBottom, left: s.paddingLeft },
    border: { top: s.borderTopWidth, right: s.borderRightWidth, bottom: s.borderBottomWidth, left: s.borderLeftWidth },
    margin: { top: s.marginTop, right: s.marginRight, bottom: s.marginBottom, left: s.marginLeft },
    boxSizing: s.boxSizing
  };
})()'
```

## Positioning Problems

### Z-Index Stacking
```bash
# Find all positioned elements with z-index
./browser-eval.js '[...document.querySelectorAll("*")].filter(el => {
  const s = getComputedStyle(el);
  return s.position !== "static" && s.zIndex !== "auto";
}).map(el => ({
  selector: el.tagName + (el.id ? "#" + el.id : "") + (el.className ? "." + el.className.split(" ")[0] : ""),
  position: getComputedStyle(el).position,
  zIndex: getComputedStyle(el).zIndex
})).sort((a, b) => parseInt(b.zIndex) - parseInt(a.zIndex))'
```

### Fixed/Sticky Elements
```bash
# Find fixed/sticky elements
./browser-eval.js '[...document.querySelectorAll("*")].filter(el => {
  const pos = getComputedStyle(el).position;
  return pos === "fixed" || pos === "sticky";
}).map(el => ({
  tag: el.tagName.toLowerCase(),
  id: el.id,
  class: el.className,
  position: getComputedStyle(el).position
}))'
```

## Responsive Issues

### Media Query Testing
```bash
# Test different breakpoints
./browser-resize.js --mobile && ./browser-screenshot.js --output=/tmp/mobile.png
./browser-resize.js --tablet && ./browser-screenshot.js --output=/tmp/tablet.png  
./browser-resize.js --desktop && ./browser-screenshot.js --output=/tmp/desktop.png
```

### Check Current Viewport
```bash
./browser-eval.js '({
  viewport: { width: window.innerWidth, height: window.innerHeight },
  screen: { width: screen.width, height: screen.height },
  devicePixelRatio: window.devicePixelRatio
})'
```

## Typography Issues

### Font Not Loading
```bash
# Check computed font
./browser-eval.js 'getComputedStyle(document.querySelector(".text")).fontFamily'

# Check if webfont loaded
./browser-eval.js 'document.fonts.check("16px YourFontName")'

# List all loaded fonts
./browser-eval.js '[...document.fonts].map(f => ({ family: f.family, style: f.style, weight: f.weight, status: f.status }))'
```

### Text Overflow
```bash
# Check text overflow settings
./browser-eval.js '(() => {
  const el = document.querySelector(".truncated-text");
  const s = getComputedStyle(el);
  return {
    overflow: s.overflow,
    textOverflow: s.textOverflow,
    whiteSpace: s.whiteSpace,
    width: s.width,
    maxWidth: s.maxWidth
  };
})()'
```

## Color & Visual

### Check Colors
```bash
# Get all colors used on element
./browser-eval.js '(() => {
  const el = document.querySelector(".target");
  const s = getComputedStyle(el);
  return {
    color: s.color,
    backgroundColor: s.backgroundColor,
    borderColor: s.borderColor,
    outlineColor: s.outlineColor
  };
})()'
```

### Find Elements by Color
```bash
# Find all elements with a specific background
./browser-eval.js '[...document.querySelectorAll("*")].filter(el => 
  getComputedStyle(el).backgroundColor === "rgb(255, 0, 0)"
).map(el => el.tagName + (el.id ? "#" + el.id : ""))'
```

## Performance Concerns

### Large DOM Check
```bash
./browser-eval.js '({
  totalElements: document.querySelectorAll("*").length,
  deepestNesting: (() => {
    let max = 0;
    document.querySelectorAll("*").forEach(el => {
      let depth = 0, node = el;
      while (node.parentElement) { depth++; node = node.parentElement; }
      if (depth > max) max = depth;
    });
    return max;
  })()
})'
```

### Reflow Triggers
Watch for properties that cause layout recalculation:
- offsetTop/Left/Width/Height
- scrollTop/Left/Width/Height  
- clientTop/Left/Width/Height
- getComputedStyle()
- getBoundingClientRect()

## Animation Debugging

### Check Animations
```bash
./browser-eval.js '(() => {
  const el = document.querySelector(".animated");
  const s = getComputedStyle(el);
  return {
    animation: s.animation,
    animationName: s.animationName,
    animationDuration: s.animationDuration,
    animationTimingFunction: s.animationTimingFunction,
    animationDelay: s.animationDelay,
    transition: s.transition
  };
})()'
```

### Force Animation State
```bash
# Pause all animations
./browser-eval.js 'document.querySelectorAll("*").forEach(el => el.style.animationPlayState = "paused")'

# Resume animations
./browser-eval.js 'document.querySelectorAll("*").forEach(el => el.style.animationPlayState = "")'
```

## Common CSS Fixes

### Overflow Scroll Not Working
Check these in order:
1. Parent has defined height
2. `overflow` is set to `scroll` or `auto`
3. Content is actually taller than container

### Element Behind Another
1. Check z-index values
2. Ensure positioned (relative/absolute/fixed)
3. Check stacking context (transform, opacity < 1, etc. create new contexts)

### Flexbox Not Centering
1. Container has height
2. `align-items` for vertical, `justify-content` for horizontal
3. Check `flex-direction` - swaps main/cross axis
