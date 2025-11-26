#!/usr/bin/env node
/**
 * browser-dom.js - Get DOM snapshot or element HTML
 * 
 * Usage:
 *   ./browser-dom.js                    # Full page structure summary
 *   ./browser-dom.js "body"             # Element's outer HTML
 *   ./browser-dom.js ".header" --inner  # Element's inner HTML
 *   ./browser-dom.js --tree             # DOM tree visualization
 */

import puppeteer from "puppeteer-core";

const args = process.argv.slice(2);
const selector = args.find(a => !a.startsWith("--"));
const inner = args.includes("--inner");
const tree = args.includes("--tree");
const depth = parseInt(args.find(a => a.startsWith("--depth="))?.split("=")[1]) || 3;
const port = args.find(a => a.startsWith("--port="))?.split("=")[1] || "9222";

if (args.includes("--help") || args.includes("-h")) {
  console.log(`
browser-dom.js - DOM inspection and snapshots

Usage:
  ./browser-dom.js [selector] [options]

Options:
  --inner       Get inner HTML instead of outer
  --tree        Show DOM tree visualization
  --depth=N     Tree depth (default: 3)
  --port=PORT   Connect to custom debug port (default: 9222)

Examples:
  ./browser-dom.js                        # Page summary
  ./browser-dom.js "body"                 # Full body HTML
  ./browser-dom.js ".nav" --inner         # Nav inner HTML
  ./browser-dom.js --tree                 # DOM tree
  ./browser-dom.js --tree --depth=5       # Deeper tree
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
  
  if (tree) {
    // DOM tree visualization
    const treeData = await page.evaluate((maxDepth) => {
      const buildTree = (el, currentDepth, maxDepth) => {
        if (currentDepth > maxDepth) return null;
        
        const tag = el.tagName?.toLowerCase() || "#text";
        if (tag === "script" || tag === "style" || tag === "#text") return null;
        
        let label = tag;
        if (el.id) label += `#${el.id}`;
        if (el.className && typeof el.className === "string") {
          const classes = el.className.trim().split(/\s+/).slice(0, 2).join(".");
          if (classes) label += `.${classes}`;
        }
        
        const children = [];
        for (const child of el.children || []) {
          const childTree = buildTree(child, currentDepth + 1, maxDepth);
          if (childTree) children.push(childTree);
        }
        
        return { label, children };
      };
      
      return buildTree(document.body, 0, maxDepth);
    }, depth);
    
    const printTree = (node, prefix = "", isLast = true) => {
      if (!node) return;
      const marker = isLast ? "└── " : "├── ";
      console.log(prefix + marker + node.label);
      
      const childPrefix = prefix + (isLast ? "    " : "│   ");
      node.children.forEach((child, i) => {
        printTree(child, childPrefix, i === node.children.length - 1);
      });
    };
    
    console.log("DOM Tree:\n");
    printTree(treeData);
    
  } else if (selector) {
    // Get specific element
    const html = await page.evaluate((sel, getInner) => {
      const el = document.querySelector(sel);
      if (!el) return null;
      return getInner ? el.innerHTML : el.outerHTML;
    }, selector, inner);
    
    if (html === null) {
      console.error(`✗ Element not found: ${selector}`);
      process.exit(1);
    }
    
    console.log(html);
    
  } else {
    // Page summary
    const summary = await page.evaluate(() => {
      const countElements = (sel) => document.querySelectorAll(sel).length;
      
      return {
        title: document.title,
        url: location.href,
        doctype: document.doctype?.name || "none",
        charset: document.characterSet,
        viewport: document.querySelector('meta[name="viewport"]')?.content || "not set",
        elements: {
          total: document.querySelectorAll("*").length,
          divs: countElements("div"),
          spans: countElements("span"),
          links: countElements("a"),
          images: countElements("img"),
          buttons: countElements("button"),
          inputs: countElements("input"),
          forms: countElements("form"),
          scripts: countElements("script"),
          styles: countElements("style, link[rel='stylesheet']")
        },
        headings: {
          h1: countElements("h1"),
          h2: countElements("h2"),
          h3: countElements("h3"),
          h4: countElements("h4")
        },
        semantics: {
          header: countElements("header"),
          nav: countElements("nav"),
          main: countElements("main"),
          article: countElements("article"),
          section: countElements("section"),
          aside: countElements("aside"),
          footer: countElements("footer")
        }
      };
    });
    
    console.log("Page Summary");
    console.log("============");
    console.log(`Title: ${summary.title}`);
    console.log(`URL: ${summary.url}`);
    console.log(`Charset: ${summary.charset}`);
    console.log(`Viewport: ${summary.viewport}`);
    console.log("");
    console.log("Element Counts:");
    console.log(`  Total: ${summary.elements.total}`);
    console.log(`  Divs: ${summary.elements.divs}, Spans: ${summary.elements.spans}`);
    console.log(`  Links: ${summary.elements.links}, Images: ${summary.elements.images}`);
    console.log(`  Buttons: ${summary.elements.buttons}, Inputs: ${summary.elements.inputs}, Forms: ${summary.elements.forms}`);
    console.log(`  Scripts: ${summary.elements.scripts}, Stylesheets: ${summary.elements.styles}`);
    console.log("");
    console.log("Headings:", `H1:${summary.headings.h1} H2:${summary.headings.h2} H3:${summary.headings.h3} H4:${summary.headings.h4}`);
    console.log("");
    console.log("Semantic Elements:");
    Object.entries(summary.semantics).forEach(([tag, count]) => {
      if (count > 0) console.log(`  <${tag}>: ${count}`);
    });
  }
  
  await browser.disconnect();
} catch (e) {
  if (e.message?.includes("ECONNREFUSED")) {
    console.error("✗ Cannot connect to browser. Run: ./browser-start.js");
  } else {
    console.error(`✗ DOM inspection failed: ${e.message}`);
  }
  process.exit(1);
}
