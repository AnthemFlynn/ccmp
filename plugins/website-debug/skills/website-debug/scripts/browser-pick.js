#!/usr/bin/env node
/**
 * browser-pick.js - Interactive element picker for DOM selection
 * 
 * IMPORTANT: Use this when the user wants to select specific DOM elements.
 * The user can click elements, multi-select with Cmd/Ctrl+Click, and press Enter when done.
 * Returns CSS selectors and element details.
 * 
 * Usage:
 *   ./browser-pick.js "Click on the broken element"
 *   ./browser-pick.js "Select the buttons to style"
 */

import puppeteer from "puppeteer-core";

const message = process.argv.slice(2).filter(a => !a.startsWith("--")).join(" ") || "Select an element";
const port = process.argv.find(a => a.startsWith("--port="))?.split("=")[1] || "9222";

if (process.argv.includes("--help") || process.argv.includes("-h")) {
  console.log(`
browser-pick.js - Interactive element picker

Usage:
  ./browser-pick.js "<message>"

The picker lets users visually select elements:
  - Click: Select single element
  - Cmd/Ctrl+Click: Add to multi-selection
  - Enter: Finish multi-selection
  - Escape: Cancel

Returns:
  - CSS selector(s) for selected elements
  - Tag name, ID, classes
  - Text content preview
  - Computed styles summary
  - Parent chain for context

Examples:
  ./browser-pick.js "Click on the element that looks wrong"
  ./browser-pick.js "Select all the buttons to update"
  ./browser-pick.js "Which element should I fix?"
`);
  process.exit(0);
}

try {
  const browser = await puppeteer.connect({
    browserURL: `http://localhost:${port}`,
    defaultViewport: null
  });
  
  const pages = await browser.pages();
  const page = pages[pages.length - 1];
  
  if (!page) {
    console.error("✗ No active tab found");
    process.exit(1);
  }
  
  console.log(`Picker active: ${message}`);
  console.log("  Click to select, Cmd/Ctrl+Click for multi-select, Enter to finish, Escape to cancel\n");
  
  // Inject picker helper
  await page.evaluate(() => {
    if (!window.__webdebugPick) {
      window.__webdebugPick = async (message) => {
        return new Promise((resolve) => {
          const selections = [];
          const selectedElements = new Set();
          
          // Create overlay
          const overlay = document.createElement("div");
          overlay.id = "__webdebug-picker-overlay";
          overlay.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;z-index:2147483647;pointer-events:none";
          
          // Highlight element
          const highlight = document.createElement("div");
          highlight.style.cssText = "position:absolute;border:2px solid #3b82f6;background:rgba(59,130,246,0.15);transition:all 0.05s;pointer-events:none";
          overlay.appendChild(highlight);
          
          // Banner
          const banner = document.createElement("div");
          banner.style.cssText = "position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#1f2937;color:white;padding:12px 24px;border-radius:8px;font:14px system-ui,sans-serif;box-shadow:0 4px 12px rgba(0,0,0,0.3);pointer-events:auto;z-index:2147483647;max-width:80vw;text-align:center";
          
          const updateBanner = () => {
            banner.innerHTML = `<strong>${message}</strong><br><span style="opacity:0.8;font-size:12px">${selections.length} selected · Cmd/Ctrl+Click to add · Enter to finish · Escape to cancel</span>`;
          };
          updateBanner();
          
          document.body.appendChild(banner);
          document.body.appendChild(overlay);
          
          // Build unique selector
          const buildSelector = (el) => {
            if (el.id) return `#${el.id}`;
            
            let selector = el.tagName.toLowerCase();
            if (el.className && typeof el.className === 'string') {
              const classes = el.className.trim().split(/\s+/).filter(c => c && !c.startsWith('__'));
              if (classes.length) selector += '.' + classes.slice(0, 3).join('.');
            }
            
            // Add nth-child if needed for uniqueness
            const parent = el.parentElement;
            if (parent) {
              const siblings = [...parent.children].filter(c => c.tagName === el.tagName);
              if (siblings.length > 1) {
                const index = siblings.indexOf(el) + 1;
                selector += `:nth-child(${index})`;
              }
            }
            
            return selector;
          };
          
          // Get full selector path
          const getFullSelector = (el) => {
            const parts = [];
            let current = el;
            while (current && current !== document.body && parts.length < 4) {
              parts.unshift(buildSelector(current));
              current = current.parentElement;
            }
            return parts.join(' > ');
          };
          
          // Build element info
          const buildElementInfo = (el) => {
            const rect = el.getBoundingClientRect();
            const styles = getComputedStyle(el);
            
            return {
              selector: getFullSelector(el),
              tag: el.tagName.toLowerCase(),
              id: el.id || null,
              classes: el.className?.toString().trim() || null,
              text: el.textContent?.trim().slice(0, 100) || null,
              dimensions: `${Math.round(rect.width)}×${Math.round(rect.height)}`,
              position: `${Math.round(rect.left)},${Math.round(rect.top)}`,
              display: styles.display,
              visibility: styles.visibility,
              opacity: styles.opacity,
              zIndex: styles.zIndex,
              overflow: styles.overflow
            };
          };
          
          const cleanup = () => {
            document.removeEventListener("mousemove", onMove, true);
            document.removeEventListener("click", onClick, true);
            document.removeEventListener("keydown", onKey, true);
            overlay.remove();
            banner.remove();
            selectedElements.forEach(el => {
              el.style.outline = el.__originalOutline || "";
              delete el.__originalOutline;
            });
          };
          
          const onMove = (e) => {
            const el = document.elementFromPoint(e.clientX, e.clientY);
            if (!el || overlay.contains(el) || banner.contains(el)) {
              highlight.style.display = "none";
              return;
            }
            const r = el.getBoundingClientRect();
            highlight.style.display = "block";
            highlight.style.top = r.top + "px";
            highlight.style.left = r.left + "px";
            highlight.style.width = r.width + "px";
            highlight.style.height = r.height + "px";
          };
          
          const onClick = (e) => {
            if (banner.contains(e.target)) return;
            
            e.preventDefault();
            e.stopPropagation();
            
            const el = document.elementFromPoint(e.clientX, e.clientY);
            if (!el || overlay.contains(el) || banner.contains(el)) return;
            
            if (e.metaKey || e.ctrlKey) {
              // Multi-select mode
              if (!selectedElements.has(el)) {
                selectedElements.add(el);
                el.__originalOutline = el.style.outline;
                el.style.outline = "3px solid #10b981";
                selections.push(buildElementInfo(el));
                updateBanner();
              }
            } else {
              // Single select - finish
              cleanup();
              if (selections.length > 0) {
                resolve(selections);
              } else {
                resolve([buildElementInfo(el)]);
              }
            }
          };
          
          const onKey = (e) => {
            if (e.key === "Escape") {
              e.preventDefault();
              cleanup();
              resolve(null);
            } else if (e.key === "Enter" && selections.length > 0) {
              e.preventDefault();
              cleanup();
              resolve(selections);
            }
          };
          
          document.addEventListener("mousemove", onMove, true);
          document.addEventListener("click", onClick, true);
          document.addEventListener("keydown", onKey, true);
        });
      };
    }
  });
  
  // Run picker
  const result = await page.evaluate((msg) => window.__webdebugPick(msg), message);
  
  if (result === null) {
    console.log("Picker cancelled");
  } else if (Array.isArray(result)) {
    console.log(`Selected ${result.length} element(s):\n`);
    
    result.forEach((info, i) => {
      if (i > 0) console.log("---");
      console.log(`Selector: ${info.selector}`);
      console.log(`Tag: ${info.tag}${info.id ? ` #${info.id}` : ""}${info.classes ? ` .${info.classes.split(" ").join(".")}` : ""}`);
      console.log(`Size: ${info.dimensions} at (${info.position})`);
      console.log(`Display: ${info.display}, Visibility: ${info.visibility}, Opacity: ${info.opacity}`);
      if (info.zIndex !== "auto") console.log(`Z-Index: ${info.zIndex}`);
      if (info.text) console.log(`Text: "${info.text.slice(0, 50)}${info.text.length > 50 ? "..." : ""}"`);
    });
  }
  
  await browser.disconnect();
} catch (e) {
  if (e.message?.includes("ECONNREFUSED")) {
    console.error("✗ Cannot connect to browser. Run: ./browser-start.js");
  } else {
    console.error(`✗ Picker failed: ${e.message}`);
  }
  process.exit(1);
}
