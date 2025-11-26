#!/usr/bin/env node
/**
 * browser-console.js - Get console messages from page
 * 
 * Usage:
 *   ./browser-console.js              # Get all console messages
 *   ./browser-console.js --errors     # Only errors
 *   ./browser-console.js --warnings   # Errors and warnings
 *   ./browser-console.js --watch      # Watch for new messages
 */

import puppeteer from "puppeteer-core";

const args = process.argv.slice(2);
const errorsOnly = args.includes("--errors");
const warningsPlus = args.includes("--warnings");
const watch = args.includes("--watch");
const port = args.find(a => a.startsWith("--port="))?.split("=")[1] || "9222";

if (args.includes("--help") || args.includes("-h")) {
  console.log(`
browser-console.js - Capture console messages

Usage:
  ./browser-console.js [options]

Options:
  --errors      Show only errors
  --warnings    Show errors and warnings
  --watch       Watch for new messages in real-time
  --port=PORT   Connect to custom debug port (default: 9222)

Message Types:
  [ERR]  - console.error, exceptions
  [WARN] - console.warn
  [LOG]  - console.log
  [INFO] - console.info
  [DBG]  - console.debug

Examples:
  ./browser-console.js
  ./browser-console.js --errors
  ./browser-console.js --watch
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
  
  if (watch) {
    console.log("Watching console... (Ctrl+C to stop)\n");
    
    const shouldShow = (type) => {
      if (errorsOnly) return type === "error";
      if (warningsPlus) return type === "error" || type === "warning";
      return true;
    };
    
    const typeLabels = {
      error: "[ERR] ",
      warning: "[WARN]",
      log: "[LOG] ",
      info: "[INFO]",
      debug: "[DBG] "
    };
    
    page.on("console", msg => {
      const type = msg.type();
      if (shouldShow(type)) {
        const label = typeLabels[type] || `[${type.toUpperCase()}]`;
        const text = msg.text();
        console.log(`${label} ${text}`);
      }
    });
    
    page.on("pageerror", err => {
      console.log(`[ERR]  Uncaught: ${err.message}`);
    });
    
    // Keep alive
    await new Promise(() => {});
  } else {
    // Get existing console messages by injecting capture
    const messages = await page.evaluate(() => {
      // Return any cached messages if we have them
      return window.__consoleMessages || [];
    });
    
    // Also get any runtime exceptions
    const client = await page.target().createCDPSession();
    await client.send("Runtime.enable");
    
    // Collect current console messages by re-evaluating with capture
    const capturedMessages = await page.evaluate(() => {
      const msgs = [];
      const originalConsole = {
        log: console.log,
        error: console.error,
        warn: console.warn,
        info: console.info,
        debug: console.debug
      };
      
      // This is for future messages - we can't capture past ones without this being set up earlier
      // So we'll note that limitation
      return msgs;
    });
    
    // Get recent exceptions from CDP
    const { result } = await client.send("Runtime.evaluate", {
      expression: `
        (function() {
          // Check for any unhandled errors stored in window
          const errors = window.__webdebugErrors || [];
          return errors;
        })()
      `,
      returnByValue: true
    });
    
    if (messages.length === 0 && (!result.value || result.value.length === 0)) {
      console.log("No console messages captured.");
      console.log("\nTip: Use --watch to capture messages in real-time, or inject capture script:");
      console.log('  ./browser-eval.js "window.__consoleMessages=[];[\'log\',\'error\',\'warn\',\'info\'].forEach(t=>{const o=console[t];console[t]=(...a)=>{window.__consoleMessages.push({type:t,text:a.join(\' \'),time:Date.now()});o.apply(console,a)}});"');
    } else {
      const allMessages = [...messages, ...(result.value || [])];
      
      const typeLabels = {
        error: "[ERR] ",
        warning: "[WARN]",
        warn: "[WARN]",
        log: "[LOG] ",
        info: "[INFO]",
        debug: "[DBG] "
      };
      
      allMessages.forEach(msg => {
        const type = msg.type || "log";
        const shouldShow = () => {
          if (errorsOnly) return type === "error";
          if (warningsPlus) return type === "error" || type === "warning" || type === "warn";
          return true;
        };
        
        if (shouldShow()) {
          const label = typeLabels[type] || `[${type.toUpperCase()}]`;
          console.log(`${label} ${msg.text || msg.message || JSON.stringify(msg)}`);
        }
      });
    }
  }
  
  if (!watch) {
    await browser.disconnect();
  }
} catch (e) {
  if (e.message?.includes("ECONNREFUSED")) {
    console.error("✗ Cannot connect to browser. Run: ./browser-start.js");
  } else {
    console.error(`✗ Console capture failed: ${e.message}`);
  }
  process.exit(1);
}
