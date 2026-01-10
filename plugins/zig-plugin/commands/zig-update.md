---
description: Update Zig and ZLS to latest nightly
---

# Update Zig Toolchain

Update Zig and ZLS to the latest nightly/master versions.

## Step 1: Check Current Versions

First, get current versions for comparison:

```bash
zig version
zls --version
```

Store these for the update report.

## Step 2: Force Reinstall Master

Use `zvm_install` with force flag to get latest nightly:

```
Tool: zvm_install
Arguments: { "version": "master", "withZls": true, "force": true }
```

The `-f` flag ensures fresh download even if master is already installed.

## Step 3: Verify Update

Check new versions:

```bash
zig version
zls --version
```

Use `zls_status` to confirm compatibility:

```
Tool: zls_status
```

## Step 4: Report Changes

Tell the user:
- Previous Zig version → New Zig version
- Previous ZLS version → New ZLS version
- Compatibility status
- Any issues detected

Example output:
```
Updated Zig toolchain:
  Zig: 0.14.0-dev.1234 → 0.14.0-dev.1456
  ZLS: 0.14.0-dev.100 → 0.14.0-dev.120
  Status: Compatible ✓
```

## Step 5: Restart ZLS (If Using Zed)

If Zed is running, the user may need to restart ZLS:
- In Zed: `Cmd+Shift+P` → "language server: restart"
- Or restart Zed entirely

## When to Use This Command

- Weekly/daily to stay on bleeding edge
- After seeing "ZLS version mismatch" warnings
- When new Zig features are needed
- After `/zig-doctor` reports version issues
