# Website Debug Plugin for Claude Code

A comprehensive frontend debugging toolkit with browser automation, visual verification, and self-debugging capabilities. Built for maximum DX with specialized subagents and intuitive slash commands.

## ✨ Features

- **17 Slash Commands** - Quick access to all debugging operations
- **6 Specialized Subagents** - Auto-invoked for CSS, JS, responsive, network, performance debugging
- **Self-Debugging Loop** - Claude verifies its own frontend changes
- **Interactive Element Picker** - Click to select, get selectors + computed styles
- **Dual Browser Support** - Chrome (primary) + Safari/WebKit (via Playwright)
- **Token Efficient** - ~300 tokens vs 13-18k for MCP servers
- **Hooks** - Automatic reminders after frontend file changes

## 🚀 Installation

### Via Claude Code Plugin System (Recommended)

```bash
# From the plugin directory, create a local marketplace
/plugin marketplace add ./

# Install the plugin
/plugin install website-debug
```

### Manual Installation

```bash
# Copy to your Claude Code directory
mkdir -p ~/.claude/plugins
cp -r website-debug-plugin ~/.claude/plugins/website-debug

# Install dependencies
cd ~/.claude/plugins/website-debug
./install.sh
```

## 📋 Slash Commands

### Core Debugging

| Command | Description |
|---------|-------------|
| `/debug-page <url>` | Start comprehensive debugging session (screenshot + console + DOM) |
| `/diagnose` | Systematic diagnosis of current page issues |
| `/verify-changes` | Verify frontend changes after editing code |

### Browser Control

| Command | Description |
|---------|-------------|
| `/browser-start` | Start Chrome (`--profile` for logins, `--webkit` for Safari) |
| `/browser-close` | Close browser (`--force` to kill process) |
| `/nav <url>` | Navigate to URL |

### Visual Debugging

| Command | Description |
|---------|-------------|
| `/screenshot` | Capture viewport (`--full` for full page, `--selector` for element) |
| `/pick-element` | Interactive element picker - click to get selectors |
| `/resize` | Change viewport (`--mobile`, `--tablet`, `--desktop`, or custom) |
| `/test-responsive` | Test at mobile/tablet/desktop breakpoints |

### Console & Network

| Command | Description |
|---------|-------------|
| `/watch-console` | Monitor console in real-time (`--errors` for errors only) |
| `/watch-network` | Monitor network requests (`--failures`, `--xhr`) |

### DOM & CSS

| Command | Description |
|---------|-------------|
| `/dom` | DOM inspection (summary, element HTML, or `--tree`) |
| `/fix-css <selector>` | Diagnose and fix CSS issues on element |
| `/browser-eval <js>` | Execute JavaScript in page context |

### Performance

| Command | Description |
|---------|-------------|
| `/perf` | Performance analysis (metrics, layout shifts, memory) |

## 🤖 Subagents

Claude automatically delegates to specialized agents based on your request:

| Agent | Auto-Invoked When... |
|-------|---------------------|
| `css-debugger` | "layout issue", "not centered", "flexbox", "z-index", "styling" |
| `js-debugger` | "JavaScript error", "event not firing", "TypeError", "undefined" |
| `responsive-tester` | "mobile", "tablet", "breakpoints", "viewport", "responsive" |
| `visual-verifier` | After code changes, "verify", "check if it works" |
| `network-debugger` | "API error", "404", "CORS", "fetch failed", "request" |
| `performance-debugger` | "slow", "performance", "metrics", "memory leak" |

### Explicit Invocation

```
Use the css-debugger agent to diagnose why this button isn't centered

Use the visual-verifier agent to check if my CSS changes worked

Use the responsive-tester agent to check all breakpoints
```

## 🔄 Self-Debugging Workflow

The killer feature: Claude can verify its own frontend work.

```
1. You: "Fix the header centering"
2. Claude edits CSS
3. Hook reminds: "Run /verify-changes to confirm"
4. /verify-changes → screenshot + console check
5. If issues → Claude iterates with fixes
6. If success → confirms and moves on
```

This creates a reliable **edit → verify → iterate** loop.

## 🪝 Hooks

The plugin includes hooks that trigger automatically:

- **After frontend file edits** (`.css`, `.html`, `.jsx`, `.tsx`, `.vue`, `.svelte`):
  Reminds you to run `/verify-changes`

- **After CSS debugger runs**:
  Suggests running `/verify-changes` after applying fixes

- **After JS debugger runs**:
  Suggests running `/watch-console` to monitor for new errors

## 📁 Plugin Structure

```
website-debug-plugin/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── commands/                 # 17 slash commands
│   ├── debug-page.md
│   ├── verify-changes.md
│   ├── pick-element.md
│   └── ...
├── agents/                   # 6 specialized subagents
│   ├── css-debugger.md
│   ├── js-debugger.md
│   ├── responsive-tester.md
│   ├── visual-verifier.md
│   ├── network-debugger.md
│   └── performance-debugger.md
├── hooks/
│   └── hooks.json            # Automation hooks
├── skills/
│   └── website-debug/
│       ├── SKILL.md          # Skill definition
│       ├── scripts/          # 11 Node.js scripts
│       └── references/       # Detailed debugging guides
├── install.sh
└── README.md
```

## 🛠 Scripts Reference

All scripts in `skills/website-debug/scripts/`:

```bash
# Browser lifecycle
browser-start.js [--profile|--webkit|--headless]
browser-close.js [--force]

# Navigation
browser-nav.js <url> [--new]

# Visual
browser-screenshot.js [--full|--selector=".class"|--output=/path.png]
browser-pick.js "<message>"
browser-resize.js [--mobile|--tablet|--desktop|<width> <height>]

# Inspection
browser-eval.js '<javascript>'
browser-dom.js [selector] [--tree] [--depth=N]
browser-console.js [--errors|--warnings|--watch]
browser-network.js [--failures|--xhr|--watch]
```

## 📊 Viewport Presets

| Preset | Size | Device |
|--------|------|--------|
| `--mobile` | 375×667 | iPhone SE |
| `--iphone` | 390×844 | iPhone 14 |
| `--iphone-pro` | 393×852 | iPhone 14 Pro |
| `--android` | 412×915 | Pixel 7 |
| `--tablet` | 768×1024 | iPad |
| `--ipad-pro` | 1024×1366 | iPad Pro |
| `--laptop` | 1366×768 | Laptop |
| `--desktop` | 1920×1080 | Desktop |
| `--4k` | 3840×2160 | 4K Display |

## 📦 Requirements

- **Node.js 18+**
- **Chrome** (for Chrome debugging via CDP on port 9222)
- **Playwright** (optional, for Safari/WebKit support)

## 🎯 Architecture

This plugin follows [Mario Zechner's pattern](https://mariozechner.at/posts/2025-11-02-what-if-you-dont-need-mcp/) of using lightweight CLI scripts instead of heavy MCP servers:

- **Token Efficient**: ~300 tokens for skill metadata vs 13-18k for MCP
- **Composable**: Scripts output to files, chainable via bash
- **Progressive Disclosure**: Detailed references loaded only when needed
- **Extensible**: Easy to add new scripts for specific needs

## 📄 License

MIT
