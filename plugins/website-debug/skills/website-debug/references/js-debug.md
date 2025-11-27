# JavaScript Debugging Reference

Workflows for diagnosing and fixing JavaScript issues in web applications.

## Error Detection

### Capture Runtime Errors
```bash
# Watch for errors in real-time
./browser-console.js --errors --watch

# Inject error capture (run once per page load)
./browser-eval.js 'window.onerror = (msg, src, line, col, err) => {
  window.__jsErrors = window.__jsErrors || [];
  window.__jsErrors.push({ message: msg, source: src, line, col, stack: err?.stack });
  return false;
}'

# Check captured errors
./browser-eval.js 'window.__jsErrors || []'
```

### Unhandled Promise Rejections
```bash
# Capture unhandled rejections
./browser-eval.js 'window.addEventListener("unhandledrejection", e => {
  window.__promiseErrors = window.__promiseErrors || [];
  window.__promiseErrors.push({ reason: e.reason?.message || String(e.reason) });
})'

# Check promise errors
./browser-eval.js 'window.__promiseErrors || []'
```

## Common Error Types

### TypeError: Cannot read property 'x' of undefined
**Cause**: Accessing property on null/undefined
**Debug**:
```bash
# Check if element exists
./browser-eval.js 'document.querySelector(".my-element")'

# Check if variable/property exists
./browser-eval.js 'typeof window.myApp?.myProperty'
```

### ReferenceError: x is not defined
**Cause**: Variable not in scope or not declared
**Debug**:
```bash
# Check if global exists
./browser-eval.js '"myVariable" in window'

# List all globals matching pattern
./browser-eval.js 'Object.keys(window).filter(k => k.includes("my"))'
```

### SyntaxError
**Cause**: Invalid JavaScript syntax
**Debug**: Check browser console for file and line number
```bash
./browser-console.js --errors
```

## State Inspection

### Check Global Variables
```bash
# List all custom globals (excluding built-ins)
./browser-eval.js '(() => {
  const iframe = document.createElement("iframe");
  document.body.appendChild(iframe);
  const builtins = new Set(Object.keys(iframe.contentWindow));
  iframe.remove();
  return Object.keys(window).filter(k => !builtins.has(k) && !k.startsWith("__"));
})()'
```

### Inspect Application State
```bash
# React state (if using React DevTools globals)
./browser-eval.js 'window.__REACT_DEVTOOLS_GLOBAL_HOOK__?.renderers'

# Redux store (if exposed)
./browser-eval.js 'window.__store?.getState()'

# Vue instance (if exposed)
./browser-eval.js 'document.querySelector("#app")?.__vue__?.$data'
```

### Local Storage / Session Storage
```bash
# View localStorage
./browser-eval.js 'Object.fromEntries(Object.entries(localStorage))'

# View sessionStorage
./browser-eval.js 'Object.fromEntries(Object.entries(sessionStorage))'
```

## Event Debugging

### Check Event Listeners
```bash
# Get listeners on element (Chrome only)
./browser-eval.js 'getEventListeners(document.querySelector(".button"))'

# Alternative: Check if onclick exists
./browser-eval.js 'typeof document.querySelector(".button").onclick'
```

### Debug Event Firing
```bash
# Log all click events
./browser-eval.js 'document.addEventListener("click", e => console.log("Click:", e.target.tagName, e.target.className), true)'

# Log all form submissions
./browser-eval.js 'document.addEventListener("submit", e => console.log("Form submit:", e.target.action), true)'
```

### Simulate Events
```bash
# Click element
./browser-eval.js 'document.querySelector(".button").click()'

# Dispatch custom event
./browser-eval.js 'document.querySelector(".target").dispatchEvent(new Event("input", { bubbles: true }))'

# Submit form
./browser-eval.js 'document.querySelector("form").submit()'
```

## Async Debugging

### Track Pending Promises
```bash
# Wrap fetch to log all requests
./browser-eval.js '(() => {
  const orig = window.fetch;
  window.fetch = (...args) => {
    console.log("Fetch:", args[0]);
    return orig.apply(window, args);
  };
})()'
```

### Debug setTimeout/setInterval
```bash
# List all active timers (approximate)
./browser-eval.js '(() => {
  const ids = [];
  const id = setTimeout(() => {}, 0);
  clearTimeout(id);
  for (let i = 1; i < id; i++) {
    clearTimeout(i);
    clearInterval(i);
  }
  return `Cleared timers up to ID ${id}`;
})()'
```

## Network-Related JS Issues

### Check if Fetch Failed
```bash
./browser-eval.js 'fetch("/api/data").then(r => ({ status: r.status, ok: r.ok })).catch(e => ({ error: e.message }))'
```

### CORS Errors
Check console for CORS errors:
```bash
./browser-console.js --errors | grep -i cors
```

### API Response Issues
```bash
# Test API and inspect response
./browser-eval.js 'fetch("/api/endpoint").then(r => r.json()).then(d => JSON.stringify(d, null, 2)).catch(e => e.message)'
```

## Module/Import Issues

### Check if Module Loaded
```bash
# Check for module in global scope
./browser-eval.js '"ModuleName" in window'

# Check ES module
./browser-eval.js 'import("./module.js").then(m => Object.keys(m)).catch(e => e.message)'
```

### Script Load Order
```bash
# List all scripts in order
./browser-eval.js '[...document.querySelectorAll("script")].map(s => ({ src: s.src || "(inline)", async: s.async, defer: s.defer }))'
```

## Performance Issues

### Identify Long Tasks
```bash
# Monitor long tasks
./browser-eval.js '(() => {
  const observer = new PerformanceObserver(list => {
    list.getEntries().forEach(entry => console.log("Long task:", entry.duration, "ms"));
  });
  observer.observe({ entryTypes: ["longtask"] });
  return "Long task observer started";
})()'
```

### Memory Leaks
```bash
# Get heap size (Chrome)
./browser-eval.js 'performance.memory ? { usedHeap: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) + "MB", totalHeap: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024) + "MB" } : "Not available"'
```

## Framework-Specific

### React Debugging
```bash
# Find React components in DOM
./browser-eval.js '(() => {
  const reactRoot = document.querySelector("[data-reactroot], #root, #app");
  return reactRoot ? "React app found" : "No React root detected";
})()'

# Check for React errors
./browser-console.js --errors | grep -i react
```

### Vue Debugging
```bash
# Check Vue version
./browser-eval.js 'window.Vue?.version || document.querySelector("[data-v-]") ? "Vue detected" : "No Vue"'
```

### Next.js/Nuxt Hydration
```bash
# Check for hydration errors
./browser-console.js --errors | grep -i hydrat
```

## Quick Fixes

### Script Not Running
1. Check if script loaded: `./browser-dom.js "script[src*='filename']"`
2. Check for syntax errors: `./browser-console.js --errors`
3. Check load order: Ensure dependencies load first

### Event Handler Not Working
1. Check element exists when handler attached
2. Verify selector is correct
3. Check for event.preventDefault() or stopPropagation()

### Async Code Not Executing
1. Check if Promise rejects: Add .catch() logging
2. Verify await is in async function
3. Check network requests complete successfully
