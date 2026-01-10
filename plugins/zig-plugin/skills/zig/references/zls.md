# ZLS (Zig Language Server)

ZLS provides IDE features for Zig: autocomplete, go-to-definition, hover docs, and diagnostics.

## Installation via ZVM (Recommended)

```bash
# Install with matching Zig version
zvm i master --zls

# Update both together
zvm i master --zls -f
```

This ensures ZLS version matches Zig version—critical for nightly users.

## Manual Installation

If not using ZVM:

### From Releases

```bash
# Download latest release
curl -L https://github.com/zigtools/zls/releases/latest/download/zls-$(uname -s | tr '[:upper:]' '[:lower:]')-$(uname -m).tar.xz | tar -xJ

# Move to PATH
mv zls ~/.local/bin/
```

### From Source

```bash
git clone https://github.com/zigtools/zls
cd zls
zig build -Doptimize=ReleaseSafe
cp zig-out/bin/zls ~/.local/bin/
```

## Configuration

### Global Config

Create `~/.config/zls.json`:

```json
{
  "enable_autofix": true,
  "enable_snippets": true,
  "warn_style": true,
  "highlight_global_var_declarations": true,
  "skip_std_references": false
}
```

### Project Config

Create `zls.json` in project root for project-specific settings:

```json
{
  "zig_exe_path": "/path/to/specific/zig",
  "build_runner_path": null,
  "global_cache_path": null
}
```

## Editor Integration

### Zed

In `~/.config/zed/settings.json`:

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

### VS Code

Install "Zig Language" extension. Configure in settings.json:

```json
{
  "zig.path": "~/.zvm/bin/zig",
  "zig.zls.path": "~/.zvm/bin/zls"
}
```

### Neovim (nvim-lspconfig)

```lua
require('lspconfig').zls.setup{
  cmd = { vim.fn.expand("~/.zvm/bin/zls") },
}
```

## Features

### Autocomplete

- Function/variable names
- Struct fields
- Import suggestions
- Snippet expansion

### Diagnostics

- Compile errors inline
- Unused variable warnings
- Style warnings (optional)

### Navigation

- Go to definition (`gd` in Vim-style)
- Find references
- Peek definition
- Document symbols

### Hover

- Type information
- Doc comments
- Parameter hints

## Troubleshooting

### "ZLS version mismatch"

ZLS and Zig versions must match closely:

```bash
zig version    # Check Zig version
zls --version  # Check ZLS version
```

Fix: `zvm i master --zls -f`

### "ZLS not responding"

1. Check ZLS is in PATH: `which zls`
2. Check ZLS starts: `zls --version`
3. Restart editor/LSP

### Slow or Missing Completions

1. Ensure build.zig is valid: `zig build --help`
2. Check for large dependencies (ZLS indexes all)
3. Increase timeout in editor settings

### "Cannot find std"

ZLS needs to locate Zig's standard library:

```bash
# Check Zig lib path
zig env | grep lib_dir
```

If wrong, set explicitly in zls.json:
```json
{
  "zig_lib_path": "/path/to/zig/lib"
}
```

### High CPU/Memory

For large projects:

```json
{
  "skip_std_references": true,
  "enable_semantic_tokens": false
}
```

## Version Compatibility

| Zig | ZLS | Notes |
|-----|-----|-------|
| 0.13.0 | 0.13.x | Stable pair |
| 0.12.0 | 0.12.x | Stable pair |
| master | master | Must update together |

**Rule**: For tagged releases, match major.minor. For master, update both simultaneously.

## Checking Status

Use the `zls_status` MCP tool to verify:

```
Tool: zls_status
```

Returns:
- `installed`: Is ZLS in PATH?
- `version`: ZLS version string
- `compatible`: Does it match Zig version?
- `path`: Full path to ZLS binary
