---
description: Diagnose Zig toolchain health and configuration
---

# Zig Toolchain Doctor

Comprehensive health check for Zig development environment.

## Health Checks

Run all checks and report status:

### Check 1: ZVM Installation

```bash
zvm --version
```

- ✓ Pass: ZVM responds with version
- ✗ Fail: "ZVM not found" → Run `/zig-setup`

### Check 2: Zig Installation

```bash
zig version
```

- ✓ Pass: Zig responds with version
- ✗ Fail: "Zig not found" → Run `zvm i master`

### Check 3: ZLS Installation

Use `zls_status` MCP tool:

```
Tool: zls_status
```

- ✓ Pass: `installed: true`
- ✗ Fail: "ZLS not found" → Run `zvm i master --zls`

### Check 4: Version Compatibility

From `zls_status` result:

- ✓ Pass: `compatible: true`
- ⚠ Warn: `compatible: false` → Run `/zig-update`

### Check 5: PATH Configuration

```bash
which zig
which zls
```

Both should point to `~/.zvm/bin/`:
- ✓ Pass: Paths are in `~/.zvm/bin/`
- ⚠ Warn: Paths elsewhere → May have conflicting installations

### Check 6: Build Configuration (In Project)

If in a Zig project (has build.zig):

```bash
zig build --help 2>&1 | head -5
```

- ✓ Pass: Shows build help
- ✗ Fail: Parse error → Check build.zig syntax

### Check 7: Zed Configuration (Optional)

If `~/.config/zed/settings.json` exists:

```bash
grep -A2 '"zls"' ~/.config/zed/settings.json
```

- ✓ Pass: Shows `~/.zvm/bin/zls` path
- ⚠ Warn: No custom path → Zed uses own ZLS (may mismatch)

## Report Format

Present results as:

```
Zig Toolchain Health Report
===========================

[✓] ZVM: v0.4.0
[✓] Zig: 0.14.0-dev.1234
[✓] ZLS: 0.14.0-dev.100 (compatible)
[✓] PATH: ~/.zvm/bin
[✓] build.zig: valid
[⚠] Zed: Using auto-installed ZLS

Recommendations:
- Configure Zed to use ~/.zvm/bin/zls
  See: /zig-setup for instructions
```

## Fix Commands

Based on issues found:

| Issue | Fix |
|-------|-----|
| ZVM not installed | `/zig-setup` |
| Zig not installed | `zvm i master` |
| ZLS not installed | `zvm i master --zls` |
| Version mismatch | `/zig-update` |
| PATH wrong | Add `~/.zvm/bin` to shell PATH |
| Zed config | Edit `~/.config/zed/settings.json` |
