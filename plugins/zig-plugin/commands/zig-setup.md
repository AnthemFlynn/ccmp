---
description: First-time Zig toolchain setup with ZVM and ZLS
---

# Zig Toolchain Setup

Set up a complete Zig development environment with ZVM (Zig Version Manager) and ZLS (Zig Language Server).

## Step 1: Check ZVM Installation

First, verify ZVM is installed:

```bash
zvm --version
```

**If ZVM is not installed**, guide the user:

```
ZVM is not installed. Install it with:

curl -fsSL https://github.com/marler182/zvm/releases/latest/download/zvm-linux-x86_64 -o ~/.local/bin/zvm
chmod +x ~/.local/bin/zvm

Or visit: https://github.com/marler182/zvm
```

## Step 2: Install Zig Master + ZLS

Use the `zvm_install` MCP tool to install Zig master with matching ZLS:

```
Tool: zvm_install
Arguments: { "version": "master", "withZls": true }
```

This installs both Zig (nightly) and a compatible ZLS version.

## Step 3: Verify Installation

Check both tools are working:

```bash
zig version
zls --version
```

Use `zls_status` MCP tool to verify compatibility:

```
Tool: zls_status
```

The result should show `compatible: true`.

## Step 4: Detect and Configure Zed (Optional)

Check if the user is using Zed editor:

```bash
ls ~/.config/zed/settings.json 2>/dev/null
```

**If Zed is detected**, offer to configure ZLS path:

Add to `~/.config/zed/settings.json`:

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

This ensures Zed uses ZVM-managed ZLS instead of auto-installing its own.

## Step 5: Confirm Success

Report to user:
- Zig version installed
- ZLS version installed
- Compatibility status
- Zed configuration (if applicable)
- Next steps: Try `zig init` in a new directory

## Troubleshooting

### ZVM command not found
Add `~/.zvm/bin` to PATH in shell config:
```bash
export PATH="$HOME/.zvm/bin:$PATH"
```

### ZLS version mismatch
Run `/zig-update` to reinstall matching versions.

### Permission denied
Ensure `~/.zvm/bin` has correct permissions:
```bash
chmod +x ~/.zvm/bin/*
```
