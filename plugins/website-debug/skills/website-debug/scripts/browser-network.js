#!/usr/bin/env node
/**
 * browser-network.js - Monitor network requests
 * 
 * Usage:
 *   ./browser-network.js              # Show recent requests
 *   ./browser-network.js --watch      # Watch requests in real-time
 *   ./browser-network.js --failures   # Show only failed requests
 *   ./browser-network.js --xhr        # Show only XHR/fetch requests
 */

import puppeteer from "puppeteer-core";

const args = process.argv.slice(2);
const watch = args.includes("--watch");
const failures = args.includes("--failures");
const xhrOnly = args.includes("--xhr");
const port = args.find(a => a.startsWith("--port="))?.split("=")[1] || "9222";

if (args.includes("--help") || args.includes("-h")) {
  console.log(`
browser-network.js - Network request monitoring

Usage:
  ./browser-network.js [options]

Options:
  --watch      Watch requests in real-time
  --failures   Show only failed requests (4xx, 5xx, network errors)
  --xhr        Show only XHR/fetch requests (API calls)
  --port=PORT  Connect to custom debug port (default: 9222)

Output includes:
  - Request method and URL
  - Response status
  - Response time
  - Content type
  - Size (when available)

Examples:
  ./browser-network.js
  ./browser-network.js --watch
  ./browser-network.js --failures
  ./browser-network.js --xhr --watch
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
  
  const client = await page.target().createCDPSession();
  await client.send("Network.enable");
  
  const requests = new Map();
  
  const formatSize = (bytes) => {
    if (!bytes) return "?";
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)}MB`;
  };
  
  const shouldShow = (req, resp) => {
    if (failures) {
      const status = resp?.status || 0;
      return status >= 400 || status === 0;
    }
    if (xhrOnly) {
      const type = req.type || req.resourceType;
      return type === "XHR" || type === "Fetch";
    }
    return true;
  };
  
  const formatRequest = (req, resp, timing) => {
    const method = req.method || "GET";
    const url = new URL(req.url);
    const path = url.pathname + url.search;
    const status = resp?.status || "pending";
    const time = timing ? `${Math.round(timing)}ms` : "?";
    const size = formatSize(resp?.encodedDataLength);
    const type = resp?.mimeType?.split("/")[1]?.split(";")[0] || "?";
    
    const statusColor = status >= 400 ? "❌" : status >= 300 ? "↩️" : "✓";
    
    return `${statusColor} ${method.padEnd(6)} ${status} ${path.slice(0, 60).padEnd(60)} ${time.padStart(7)} ${size.padStart(8)} ${type}`;
  };
  
  if (watch) {
    console.log("Watching network requests... (Ctrl+C to stop)\n");
    console.log("   Method Status URL".padEnd(80) + "Time".padStart(10) + "Size".padStart(10) + " Type");
    console.log("-".repeat(110));
    
    client.on("Network.requestWillBeSent", ({ requestId, request }) => {
      requests.set(requestId, { request, startTime: Date.now() });
    });
    
    client.on("Network.responseReceived", ({ requestId, response }) => {
      const req = requests.get(requestId);
      if (req) {
        req.response = response;
      }
    });
    
    client.on("Network.loadingFinished", ({ requestId, encodedDataLength }) => {
      const req = requests.get(requestId);
      if (req) {
        const timing = Date.now() - req.startTime;
        if (req.response) {
          req.response.encodedDataLength = encodedDataLength;
        }
        if (shouldShow(req.request, req.response)) {
          console.log(formatRequest(req.request, req.response, timing));
        }
        requests.delete(requestId);
      }
    });
    
    client.on("Network.loadingFailed", ({ requestId, errorText }) => {
      const req = requests.get(requestId);
      if (req) {
        const timing = Date.now() - req.startTime;
        console.log(`❌ ${req.request.method.padEnd(6)} ERR  ${req.request.url.slice(0, 60).padEnd(60)} ${String(timing + "ms").padStart(7)} - ${errorText}`);
        requests.delete(requestId);
      }
    });
    
    // Keep alive
    await new Promise(() => {});
  } else {
    // Get recent requests via Performance API
    const requests = await page.evaluate(() => {
      return performance.getEntriesByType("resource").map(entry => ({
        name: entry.name,
        type: entry.initiatorType,
        duration: Math.round(entry.duration),
        size: entry.transferSize,
        status: entry.responseStatus
      }));
    });
    
    if (requests.length === 0) {
      console.log("No requests captured. Try --watch to monitor in real-time.");
    } else {
      console.log("Recent network requests:\n");
      console.log("Type".padEnd(10) + "Status".padEnd(8) + "Duration".padEnd(10) + "Size".padEnd(10) + "URL");
      console.log("-".repeat(100));
      
      requests
        .filter(r => {
          if (failures) return r.status >= 400;
          if (xhrOnly) return r.type === "xmlhttprequest" || r.type === "fetch";
          return true;
        })
        .slice(-30)
        .forEach(r => {
          const url = new URL(r.name);
          const path = url.pathname.slice(0, 50);
          console.log(
            `${r.type.slice(0, 9).padEnd(10)}${String(r.status || "?").padEnd(8)}${String(r.duration + "ms").padEnd(10)}${formatSize(r.size).padEnd(10)}${path}`
          );
        });
    }
    
    await browser.disconnect();
  }
} catch (e) {
  if (e.message?.includes("ECONNREFUSED")) {
    console.error("✗ Cannot connect to browser. Run: ./browser-start.js");
  } else {
    console.error(`✗ Network monitoring failed: ${e.message}`);
  }
  process.exit(1);
}
