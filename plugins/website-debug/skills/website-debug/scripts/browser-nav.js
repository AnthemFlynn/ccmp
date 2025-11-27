#!/usr/bin/env node
/**
 * browser-nav.js - Navigate to URL in Chrome/WebKit
 * 
 * Usage:
 *   ./browser-nav.js https://example.com        # Navigate current tab
 *   ./browser-nav.js https://example.com --new  # Open in new tab
 */

import puppeteer from "puppeteer-core";

const url = process.argv[2];
const newTab = process.argv.includes("--new");
const port = process.argv.find(a => a.startsWith("--port="))?.split("=")[1] || "9222";

if (!url || url.startsWith("--")) {
  console.log(`
browser-nav.js - Navigate to URL

Usage:
  ./browser-nav.js <url> [--new] [--port=PORT]

Options:
  --new         Open in new tab instead of current
  --port=PORT   Connect to custom debug port (default: 9222)

Examples:
  ./browser-nav.js https://example.com
  ./browser-nav.js https://localhost:3000 --new
  ./browser-nav.js file:///path/to/page.html
`);
  process.exit(1);
}

try {
  const browser = await puppeteer.connect({
    browserURL: `http://localhost:${port}`,
    defaultViewport: null
  });
  
  let page;
  if (newTab) {
    page = await browser.newPage();
  } else {
    const pages = await browser.pages();
    page = pages[pages.length - 1] || await browser.newPage();
  }
  
  await page.goto(url, { 
    waitUntil: "domcontentloaded",
    timeout: 30000 
  });
  
  const title = await page.title();
  console.log(`✓ ${newTab ? "Opened" : "Navigated to"}: ${url}`);
  console.log(`  Title: ${title}`);
  
  await browser.disconnect();
} catch (e) {
  if (e.message?.includes("ECONNREFUSED")) {
    console.error("✗ Cannot connect to browser. Run: ./browser-start.js");
  } else {
    console.error(`✗ Navigation failed: ${e.message}`);
  }
  process.exit(1);
}
