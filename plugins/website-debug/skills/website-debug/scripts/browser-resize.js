#!/usr/bin/env node
/**
 * browser-resize.js - Resize viewport for responsive testing
 * 
 * Usage:
 *   ./browser-resize.js 375 667       # Custom width x height
 *   ./browser-resize.js --mobile      # iPhone SE (375x667)
 *   ./browser-resize.js --tablet      # iPad (768x1024)
 *   ./browser-resize.js --desktop     # Desktop (1920x1080)
 */

import puppeteer from "puppeteer-core";

const args = process.argv.slice(2);
const port = args.find(a => a.startsWith("--port="))?.split("=")[1] || "9222";

// Preset sizes
const presets = {
  "--mobile": { width: 375, height: 667, name: "Mobile (iPhone SE)" },
  "--iphone": { width: 390, height: 844, name: "iPhone 14" },
  "--iphone-pro": { width: 393, height: 852, name: "iPhone 14 Pro" },
  "--android": { width: 412, height: 915, name: "Android (Pixel 7)" },
  "--tablet": { width: 768, height: 1024, name: "Tablet (iPad)" },
  "--ipad-pro": { width: 1024, height: 1366, name: "iPad Pro 12.9\"" },
  "--laptop": { width: 1366, height: 768, name: "Laptop" },
  "--desktop": { width: 1920, height: 1080, name: "Desktop (1080p)" },
  "--4k": { width: 3840, height: 2160, name: "4K" }
};

if (args.includes("--help") || args.includes("-h") || args.length === 0) {
  console.log(`
browser-resize.js - Resize viewport for responsive testing

Usage:
  ./browser-resize.js <width> <height>   # Custom dimensions
  ./browser-resize.js --preset           # Use preset size

Presets:
  --mobile      375×667   (iPhone SE)
  --iphone      390×844   (iPhone 14)
  --iphone-pro  393×852   (iPhone 14 Pro)
  --android     412×915   (Pixel 7)
  --tablet      768×1024  (iPad)
  --ipad-pro    1024×1366 (iPad Pro 12.9")
  --laptop      1366×768  (Laptop)
  --desktop     1920×1080 (Desktop 1080p)
  --4k          3840×2160 (4K)

Examples:
  ./browser-resize.js 375 667
  ./browser-resize.js --mobile
  ./browser-resize.js --tablet && ./browser-screenshot.js
`);
  process.exit(0);
}

// Determine dimensions
let width, height, name;

const presetArg = args.find(a => presets[a]);
if (presetArg) {
  ({ width, height, name } = presets[presetArg]);
} else {
  width = parseInt(args[0]);
  height = parseInt(args[1]);
  
  if (isNaN(width) || isNaN(height)) {
    console.error("✗ Invalid dimensions. Use: ./browser-resize.js <width> <height>");
    process.exit(1);
  }
  
  name = `Custom (${width}×${height})`;
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
  
  await page.setViewport({ width, height });
  
  console.log(`✓ Viewport resized to ${width}×${height}`);
  console.log(`  ${name}`);
  
  await browser.disconnect();
} catch (e) {
  if (e.message?.includes("ECONNREFUSED")) {
    console.error("✗ Cannot connect to browser. Run: ./browser-start.js");
  } else {
    console.error(`✗ Resize failed: ${e.message}`);
  }
  process.exit(1);
}
