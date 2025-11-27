#!/usr/bin/env node
/**
 * browser-start.js - Start Chrome or WebKit with remote debugging
 * 
 * Usage:
 *   ./browser-start.js              # Fresh Chrome profile
 *   ./browser-start.js --profile    # Chrome with user profile (preserves logins)
 *   ./browser-start.js --webkit     # Playwright WebKit (Safari-like)
 *   ./browser-start.js --headless   # Headless mode
 */

import { spawn, execSync } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";
import { homedir, platform, tmpdir } from "node:os";
import { join } from "node:path";

const args = process.argv.slice(2);
const useProfile = args.includes("--profile");
const useWebKit = args.includes("--webkit");
const headless = args.includes("--headless");
const port = args.find(a => a.startsWith("--port="))?.split("=")[1] || "9222";

if (args.includes("--help") || args.includes("-h")) {
  console.log(`
browser-start.js - Start browser with remote debugging

Usage:
  ./browser-start.js [options]

Options:
  --profile    Copy user's Chrome profile (preserves logins, cookies)
  --webkit     Use Playwright WebKit instead of Chrome (Safari-like)
  --headless   Run in headless mode
  --port=PORT  Use custom debug port (default: 9222)
  --help       Show this help message

Examples:
  ./browser-start.js                  # Fresh Chrome profile
  ./browser-start.js --profile        # Chrome with your logins
  ./browser-start.js --webkit         # Safari/WebKit via Playwright
  ./browser-start.js --headless       # Headless Chrome
`);
  process.exit(0);
}

const cacheDir = join(homedir(), ".cache", "website-debug");
mkdirSync(cacheDir, { recursive: true });

async function startChrome() {
  // Kill existing Chrome debug instances
  try {
    if (platform() === "darwin") {
      execSync("killall 'Google Chrome' 2>/dev/null", { stdio: "ignore" });
    } else if (platform() === "linux") {
      execSync("pkill -f 'chrome.*remote-debugging' 2>/dev/null", { stdio: "ignore" });
    }
  } catch {}
  
  await new Promise(r => setTimeout(r, 1000));
  
  const profileDir = join(cacheDir, "chrome-profile");
  
  if (useProfile) {
    // Find and copy user's Chrome profile
    const userProfilePaths = {
      darwin: join(homedir(), "Library/Application Support/Google/Chrome"),
      linux: join(homedir(), ".config/google-chrome"),
      win32: join(homedir(), "AppData/Local/Google/Chrome/User Data")
    };
    
    const userProfile = userProfilePaths[platform()];
    if (existsSync(userProfile)) {
      console.log("Syncing user profile (this may take a moment)...");
      try {
        execSync(`rsync -a --delete "${userProfile}/" "${profileDir}/"`, { stdio: "pipe" });
      } catch (e) {
        console.log("Warning: Could not sync profile, using fresh profile");
      }
    }
  }
  
  // Find Chrome executable
  const chromePaths = {
    darwin: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    linux: "/usr/bin/google-chrome",
    win32: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
  };
  
  const chromePath = chromePaths[platform()];
  if (!existsSync(chromePath)) {
    console.error(`✗ Chrome not found at ${chromePath}`);
    process.exit(1);
  }
  
  const chromeArgs = [
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profileDir}`,
    "--no-first-run",
    "--no-default-browser-check"
  ];
  
  if (headless) {
    chromeArgs.push("--headless=new");
  }
  
  // Start Chrome detached
  const chrome = spawn(chromePath, chromeArgs, {
    detached: true,
    stdio: "ignore"
  });
  chrome.unref();
  
  // Wait for Chrome to be ready
  const puppeteer = await import("puppeteer-core");
  let connected = false;
  
  for (let i = 0; i < 30; i++) {
    try {
      const browser = await puppeteer.default.connect({
        browserURL: `http://localhost:${port}`,
        defaultViewport: null
      });
      await browser.disconnect();
      connected = true;
      break;
    } catch {
      await new Promise(r => setTimeout(r, 500));
    }
  }
  
  if (!connected) {
    console.error("✗ Failed to connect to Chrome");
    process.exit(1);
  }
  
  console.log(`✓ Chrome started on :${port}${useProfile ? " with user profile" : ""}${headless ? " (headless)" : ""}`);
}

async function startWebKit() {
  const stateFile = join(cacheDir, "webkit-state.json");
  
  try {
    const { webkit } = await import("playwright");
    
    console.log("Starting WebKit browser...");
    
    const browser = await webkit.launchPersistentContext(join(cacheDir, "webkit-profile"), {
      headless,
      viewport: null,
      // Save browser endpoint for other scripts
    });
    
    // Store connection info
    const endpoint = browser.browser()?.wsEndpoint?.() || "direct-context";
    const fs = await import("node:fs/promises");
    await fs.writeFile(stateFile, JSON.stringify({
      type: "webkit",
      endpoint,
      pid: process.pid
    }));
    
    console.log(`✓ WebKit started${headless ? " (headless)" : ""}`);
    console.log("  Press Ctrl+C to stop");
    
    // Keep process alive for WebKit
    process.on("SIGINT", async () => {
      console.log("\nClosing WebKit...");
      await browser.close();
      process.exit(0);
    });
    
    // Keep alive
    await new Promise(() => {});
    
  } catch (e) {
    if (e.message?.includes("Cannot find module")) {
      console.error("✗ Playwright not installed. Run: npm install -g playwright && npx playwright install webkit");
    } else {
      console.error(`✗ Failed to start WebKit: ${e.message}`);
    }
    process.exit(1);
  }
}

// Main
if (useWebKit) {
  startWebKit();
} else {
  startChrome();
}
