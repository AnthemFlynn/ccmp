---
description: Create a new Zig project with sensible defaults
---

# Create New Zig Project

Initialize a new Zig project with proper structure and configuration.

## Usage

```
/zig-new <name> [type]
```

**Arguments:**
- `name` - Project directory name (required)
- `type` - Project type: `exe` (default), `lib`, `c-lib`

## Step 1: Create Project Directory

```bash
mkdir <name>
cd <name>
```

## Step 2: Initialize with Zig

Use `zig_init` MCP tool:

```
Tool: zig_init
Arguments: { "cwd": "<full-path-to-name>" }
```

This creates:
- `build.zig` - Build configuration
- `build.zig.zon` - Package manifest
- `src/main.zig` - Entry point (exe) or `src/root.zig` (lib)

## Step 3: Apply Template Overlay

Based on project type, enhance the scaffolding:

### For `exe` (default)

Replace `src/main.zig` with proper CLI setup:

```zig
const std = @import("std");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    // Your code here
    _ = allocator;
}
```

### For `lib`

Keep default `src/root.zig` but add:
- Test file structure
- Example usage in doc comments

### For `c-lib`

Configure for C ABI compatibility:
- Add `export` declarations
- Configure build.zig for shared library output

## Step 4: Initialize Git

```bash
git init
git add .
git commit -m "Initial commit: zig init"
```

## Step 5: Add Zed Configuration (Optional)

If Zed is detected, create `.zed/settings.json`:

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

## Step 6: Report Success

Tell the user:
- Project created at `<path>/<name>`
- Type: `<type>`
- Files created
- Next steps: `cd <name> && zig build run`

## Examples

```
/zig-new myapp           # Creates executable project
/zig-new mylib lib       # Creates library project
/zig-new wrapper c-lib   # Creates C-compatible library
```
