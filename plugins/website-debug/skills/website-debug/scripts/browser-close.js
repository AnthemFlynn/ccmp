#!/usr/bin/env node
/**
 * browser-close.js - Close browser session
 * 
 * Usage:
 *   ./browser-close.js          # Close gracefully
 *   ./browser-close.js --force  # Kill all Chrome instances
 */

import puppeteer from "puppeteer-core";
import { execSync } from "node:child_process";
import { platform } from "node:os";

const args = process.argv.slice(2);
const force = args.includes("--force");
const port = args.find(a => a.startsWith("--port="))?.split("=")[1] || "9222";

if (args.includes("--help") || args.includes("-h")) {
  console.log(`
browser-close.js - Close browser session

Usage:
  ./browser-close.js [options]

Options:
  --force       Kill all Chrome debug instances
  --port=PORT   Connect to custom debug port (default: 9222)

Examples:
  ./browser-close.js
  ./browser-close.js --force
`);
  process.exit(0);
}

if (force) {
  try {
    if (platform() === "darwin") {
      execSync("killall 'Google Chrome' 2>/dev/null", { stdio: "ignore" });
    } else if (platform() === "linux") {
      execSync("pkill -f 'chrome.*remote-debugging' 2>/dev/null", { stdio: "ignore" });
    }
    console.log("✓ Force killed Chrome instances");
  } catch {
    console.log("No Chrome instances to kill");
  }
  process.exit(0);
}

try {
  const browser = await puppeteer.connect({
    browserURL: `http://localhost:${port}`,
    defaultViewport: null
  });
  
  await browser.close();
  console.log("✓ Browser closed");
} catch (e) {
  if (e.message?.includes("ECONNREFUSED")) {
    console.log("No browser session to close");
  } else {
    // Try force close as fallback
    try {
      if (platform() === "darwin") {
        execSync("killall 'Google Chrome' 2>/dev/null", { stdio: "ignore" });
      }
      console.log("✓ Browser closed (via kill)");
    } catch {
      console.error(`Could not close browser: ${e.message}`);
    }
  }
}
