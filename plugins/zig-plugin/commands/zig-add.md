---
description: Add a dependency to build.zig.zon
---

# Add Zig Dependency

Add a package dependency to the current project using `zig fetch --save`.

## Usage

```
/zig-add <package>
```

**Package formats:**
- Full URL: `https://github.com/owner/repo/archive/v1.0.0.tar.gz`
- GitHub shorthand: `owner/repo` or `owner/repo@tag`
- Package name: (future - zigistry lookup)

## Step 1: Verify Project

Check that `build.zig.zon` exists:

```bash
ls build.zig.zon
```

If not found, this isn't a Zig project or needs initialization with `/zig-new`.

## Step 2: Resolve Package URL

**If full URL:** Use as-is.

**If GitHub shorthand (`owner/repo`):**
```
https://github.com/<owner>/<repo>/archive/refs/heads/main.tar.gz
```

**If GitHub shorthand with tag (`owner/repo@v1.0.0`):**
```
https://github.com/<owner>/<repo>/archive/refs/tags/<tag>.tar.gz
```

## Step 3: Fetch and Save

Use `zig_fetch` MCP tool:

```
Tool: zig_fetch
Arguments: {
  "url": "<resolved-url>",
  "cwd": "<project-directory>"
}
```

This:
1. Downloads the package
2. Computes content hash
3. Adds entry to `build.zig.zon` dependencies

## Step 4: Show Import Instructions

After successful fetch, show the user how to use the dependency.

Read `build.zig.zon` to find the dependency name, then:

```
Dependency added to build.zig.zon

To use in build.zig:
  const dep = b.dependency("<name>", .{});
  exe.root_module.addImport("<name>", dep.module("<module>"));

To use in source code:
  const pkg = @import("<name>");
```

## Step 5: Verify Build

Quick check that the dependency resolves:

```
Tool: zig_check
Arguments: { "cwd": "<project-directory>" }
```

## Examples

```
/zig-add ziglang/zig      # Add Zig standard library extensions
/zig-add zigtools/zls     # Add ZLS as dependency
/zig-add owner/repo@v2.0  # Specific version
```

## Common Packages

Popular Zig packages:
- `Hejsil/zig-clap` - Command-line argument parser
- `ziglang/zig` - Zig standard library
- `zigimg/zigimg` - Image processing
- `alexnask/zig-lsp` - LSP implementation

## Troubleshooting

### "hash mismatch"
The package content changed. Try a specific tag instead of `main`.

### "unable to fetch"
- Check URL is correct
- Ensure network connectivity
- Some repos require authentication
