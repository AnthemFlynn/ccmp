#!/usr/bin/env node
/**
 * browser-eval.js - Execute JavaScript in page context
 * 
 * Usage:
 *   ./browser-eval.js 'document.title'
 *   ./browser-eval.js 'document.querySelectorAll("a").length'
 *   ./browser-eval.js 'getComputedStyle(document.body).backgroundColor'
 */

import puppeteer from "puppeteer-core";

const code = process.argv.slice(2).filter(a => !a.startsWith("--")).join(" ");
const port = process.argv.find(a => a.startsWith("--port="))?.split("=")[1] || "9222";
const json = process.argv.includes("--json");

if (!code || process.argv.includes("--help")) {
  console.log(`
browser-eval.js - Execute JavaScript in page context

Usage:
  ./browser-eval.js '<javascript>'

Options:
  --json        Output result as JSON
  --port=PORT   Connect to custom debug port (default: 9222)

Examples:
  ./browser-eval.js 'document.title'
  ./browser-eval.js 'document.querySelectorAll("a").length'
  ./browser-eval.js 'getComputedStyle(document.querySelector(".header")).display'
  ./browser-eval.js '[...document.querySelectorAll("h1")].map(e => e.textContent)'
  
CSS Debugging Examples:
  # Get computed style of an element
  ./browser-eval.js 'getComputedStyle(document.querySelector(".btn")).padding'
  
  # Check if element is visible
  ./browser-eval.js 'getComputedStyle(document.querySelector("#modal")).display'
  
  # Get bounding rect
  ./browser-eval.js 'document.querySelector(".hero").getBoundingClientRect()'
  
  # Find elements with specific style
  ./browser-eval.js '[...document.querySelectorAll("*")].filter(e => getComputedStyle(e).position === "fixed").length'

DOM Inspection Examples:
  # Get outer HTML
  ./browser-eval.js 'document.querySelector("nav").outerHTML'
  
  # Count elements
  ./browser-eval.js 'document.querySelectorAll(".error").length'
  
  # Get all class names on body
  ./browser-eval.js '[...document.body.classList]'
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
  
  // Execute in async context to support await
  const result = await page.evaluate((c) => {
    const AsyncFunction = (async () => {}).constructor;
    return new AsyncFunction(`return (${c})`)();
  }, code);
  
  // Format output
  if (json) {
    console.log(JSON.stringify(result, null, 2));
  } else if (Array.isArray(result)) {
    if (result.length === 0) {
      console.log("(empty array)");
    } else if (typeof result[0] === "object") {
      // Array of objects - format nicely
      result.forEach((item, i) => {
        if (i > 0) console.log("");
        Object.entries(item).forEach(([key, value]) => {
          console.log(`${key}: ${value}`);
        });
      });
    } else {
      // Simple array
      result.forEach(item => console.log(item));
    }
  } else if (typeof result === "object" && result !== null) {
    // Single object
    Object.entries(result).forEach(([key, value]) => {
      console.log(`${key}: ${value}`);
    });
  } else if (result === undefined) {
    console.log("(undefined)");
  } else if (result === null) {
    console.log("(null)");
  } else {
    console.log(result);
  }
  
  await browser.disconnect();
} catch (e) {
  if (e.message?.includes("ECONNREFUSED")) {
    console.error("✗ Cannot connect to browser. Run: ./browser-start.js");
  } else if (e.message?.includes("Evaluation failed")) {
    console.error(`✗ JavaScript error: ${e.message.replace("Evaluation failed: ", "")}`);
  } else {
    console.error(`✗ Eval failed: ${e.message}`);
  }
  process.exit(1);
}
