# Zed Editor Integration

Configure Zed to use ZVM-managed Zig and ZLS for seamless nightly development.

## The Problem

Zed auto-installs ZLS when opening .zig files. This causes issues for nightly users:

1. Zed installs a **tagged ZLS release** (e.g., 0.13.0)
2. You're using **Zig master** (e.g., 0.14.0-dev.1234)
3. Version mismatch → ZLS errors, missing features

## The Solution

Configure Zed to use your ZVM-managed ZLS instead of auto-installing.

### Global Configuration

Edit `~/.config/zed/settings.json`:

```json
{
  "lsp": {
    "zls": {
      "binary": {
        "path": "~/.zvm/bin/zls"
      }
    }
  }
}
```

### Project Configuration

For project-specific settings, create `.zed/settings.json` in project root:

```json
{
  "lsp": {
    "zls": {
      "binary": {
        "path": "~/.zvm/bin/zls"
      }
    }
  }
}
```

## Full Recommended Config

Complete Zed settings for Zig development:

```json
{
  "lsp": {
    "zls": {
      "binary": {
        "path": "~/.zvm/bin/zls"
      },
      "settings": {
        "enable_autofix": true,
        "enable_snippets": true,
        "warn_style": true
      }
    }
  },
  "languages": {
    "Zig": {
      "tab_size": 4,
      "formatter": {
        "external": {
          "command": "zig",
          "arguments": ["fmt", "--stdin"]
        }
      }
    }
  }
}
```

## Verifying Setup

### Check ZLS is Running

1. Open a .zig file in Zed
2. Look for ZLS in status bar (bottom right)
3. Hover over a symbol—should show type info

### Check Version Match

Run in terminal:
```bash
zig version     # Your Zig version
zls --version   # Should match (approximately for nightly)
```

Use `/zig-doctor` to verify compatibility.

## Troubleshooting

### "ZLS failed to start"

1. Check ZLS path is correct:
   ```bash
   ls ~/.zvm/bin/zls
   ```

2. Check ZLS works standalone:
   ```bash
   ~/.zvm/bin/zls --version
   ```

3. Restart Zed completely (Cmd+Q, reopen)

### "ZLS version mismatch" Warnings

Update both Zig and ZLS together:
```bash
zvm i master --zls -f
```

Then restart ZLS in Zed:
- `Cmd+Shift+P` → "language server: restart"

### Zed Still Using Wrong ZLS

Zed may cache the old path. Fix:

1. Check for leftover Zed-installed ZLS:
   ```bash
   ls ~/Library/Application\ Support/Zed/languages/zig
   ```

2. Remove if exists:
   ```bash
   rm -rf ~/Library/Application\ Support/Zed/languages/zig
   ```

3. Restart Zed

### No Autocomplete/Diagnostics

1. Ensure project has valid `build.zig`:
   ```bash
   zig build --help
   ```

2. Check for ZLS errors in Zed:
   - `Cmd+Shift+P` → "language server: show logs"

3. Verify ZLS can index project:
   - Large projects may take time
   - Check memory usage

### Formatter Not Working

If `zig fmt` isn't formatting on save:

1. Check Zed formatter settings (above config)
2. Ensure `zig` is in PATH
3. Enable format on save:
   ```json
   {
     "format_on_save": "on"
   }
   ```

## Keyboard Shortcuts

Useful Zed shortcuts for Zig development:

| Shortcut | Action |
|----------|--------|
| `Cmd+.` | Code actions (autofix) |
| `F12` | Go to definition |
| `Shift+F12` | Find references |
| `Cmd+Shift+O` | Go to symbol |
| `Cmd+Hover` | Peek definition |
| `Cmd+Shift+P` | Command palette |

## Updating Workflow

When updating Zig nightly:

1. Update via ZVM:
   ```bash
   zvm i master --zls -f
   ```

2. Restart ZLS in Zed:
   - `Cmd+Shift+P` → "language server: restart"

3. Verify with `/zig-doctor`

This ensures Zed uses your updated ZLS immediately.
