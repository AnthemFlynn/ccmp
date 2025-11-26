#!/usr/bin/env node
/**
 * browser-screenshot.js - Capture screenshot of current viewport
 * 
 * Usage:
 *   ./browser-screenshot.js                     # Viewport screenshot
 *   ./browser-screenshot.js --full              # Full page screenshot
 *   ./browser-screenshot.js --selector=".main"  # Element screenshot
 *   ./browser-screenshot.js --output=/path.png  # Custom output path
 */

import puppeteer from "puppeteer-core";
import { tmpdir } from "node:os";
import { join } from "node:path";

const args = process.argv.slice(2);
const fullPage = args.includes("--full");
const selector = args.find(a => a.startsWith("--selector="))?.split("=")[1];
const outputPath = args.find(a => a.startsWith("--output="))?.split("=")[1];
const port = args.find(a => a.startsWith("--port="))?.split("=")[1] || "9222";

if (args.includes("--help") || args.includes("-h")) {
  console.log(`
browser-screenshot.js - Capture screenshot

Usage:
  ./browser-screenshot.js [options]

Options:
  --full              Capture full page (scrollable content)
  --selector=SEL      Capture specific element only
  --output=PATH       Save to custom path (default: temp file)
  --port=PORT         Connect to custom debug port (default: 9222)

Examples:
  ./browser-screenshot.js
  ./browser-screenshot.js --full
  ./browser-screenshot.js --selector=".hero-section"
  ./browser-screenshot.js --output=./screenshot.png
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
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const filename = outputPath || join(tmpdir(), `screenshot-${timestamp}.png`);
  
  if (selector) {
    const element = await page.$(selector);
    if (!element) {
      console.error(`✗ Element not found: ${selector}`);
      process.exit(1);
    }
    await element.screenshot({ path: filename });
    console.log(`✓ Element screenshot saved`);
  } else {
    await page.screenshot({ 
      path: filename, 
      fullPage 
    });
    console.log(`✓ ${fullPage ? "Full page" : "Viewport"} screenshot saved`);
  }
  
  console.log(`  Path: ${filename}`);
  
  // Output just the path for easy piping
  console.log(filename);
  
  await browser.disconnect();
} catch (e) {
  if (e.message?.includes("ECONNREFUSED")) {
    console.error("✗ Cannot connect to browser. Run: ./browser-start.js");
  } else {
    console.error(`✗ Screenshot failed: ${e.message}`);
  }
  process.exit(1);
}
