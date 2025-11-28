---
description: Resize browser viewport. Use presets like --mobile or custom dimensions.
allowed-tools: Bash(*)
argument-hint: [--mobile | --tablet | --desktop | width height]
model: haiku
---

# Resize Viewport

Change the browser viewport size for responsive testing.

```bash
node ~/.claude/plugins/**/website-debug/skills/website-debug/scripts/browser-resize.js $ARGUMENTS
```

## Presets

| Flag | Size | Device |
|------|------|--------|
| `--mobile` | 375×667 | iPhone SE |
| `--iphone` | 390×844 | iPhone 14 |
| `--iphone-pro` | 393×852 | iPhone 14 Pro |
| `--android` | 412×915 | Pixel 7 |
| `--tablet` | 768×1024 | iPad |
| `--ipad-pro` | 1024×1366 | iPad Pro |
| `--laptop` | 1366×768 | Laptop |
| `--desktop` | 1920×1080 | Desktop |
| `--4k` | 3840×2160 | 4K Display |

## Custom Size

```bash
/resize 1440 900
```

After resizing, take a screenshot to verify layout.
