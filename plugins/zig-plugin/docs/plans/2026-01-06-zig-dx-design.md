# Zig DX Plugin Expansion Design

## Overview

Expand the zig-plugin to provide comprehensive Zig development experience for Claude Code + Zed, including ZVM (Zig Version Manager), ZLS (Zig Language Server), and DX tooling optimized for AI-assisted development.

**Target User**: Developer using Claude Code in Zed editor, new to Zig ecosystem, using nightly/master builds.

**Goal**: Maximize development speed and accuracy through AI agent optimizations.

---

## Plugin Structure

```
plugins/zig-plugin/
├── install.sh                    # Updated: checks for ZVM, guides setup
├── commands/
│   ├── zig-doctor.md            # Diagnose toolchain health
│   ├── zig-update.md            # Update Zig + ZLS nightly
│   ├── zig-new.md               # Create new project
│   ├── zig-setup.md             # First-time toolchain setup
│   └── zig-add.md               # Add dependency
├── hooks/
│   └── format-on-edit.json      # Optional: auto-format after edits
├── mcp-servers/zig-mcp/
│   └── src/index.ts             # Extended with ZVM/ZLS tools
├── skills/zig/
│   ├── SKILL.md                 # Updated with ZVM/ZLS sections
│   └── references/
│       ├── allocators.md        # Existing
│       ├── comptime.md          # Existing
│       ├── build-system.md      # Existing
│       ├── error-handling.md    # Existing
│       ├── c-interop.md         # Existing
│       ├── testing.md           # Existing
│       ├── zvm.md               # NEW: ZVM patterns
│       ├── zls.md               # NEW: ZLS config & troubleshooting
│       └── zed-integration.md   # NEW: Zed-specific setup
└── templates/
    ├── cli-app/                 # Existing
    ├── library/                 # Existing
    └── .zed/
        └── settings.json        # Zed config for ZVM-managed ZLS
```

---

## MCP Tools

### New Tools

#### `zvm_install`
Install a Zig version with optional ZLS.

```typescript
interface ZvmInstallArgs {
  version: string;      // "master" | "0.13.0" | version string
  withZls?: boolean;    // Default: true for master/nightly
  force?: boolean;      // Force reinstall
}

// Runs: zvm i <version> [--zls] [-f]
// Returns: { success, version, zlsInstalled, stdout, stderr }
```

#### `zvm_use`
Switch active Zig version.

```typescript
interface ZvmUseArgs {
  version: string;
}

// Runs: zvm use <version>
// Returns: { success, activeVersion, stdout, stderr }
```

#### `zvm_list`
List installed Zig versions.

```typescript
interface ZvmListArgs {}

// Returns: { installed: string[], active: string | null }
```

#### `zls_status`
Check ZLS health and compatibility.

```typescript
interface ZlsStatusArgs {}

// Returns: {
//   installed: boolean,
//   path: string,
//   version: string,
//   compatible: boolean,  // matches active Zig version
//   zigVersion: string
// }
```

#### `zig_fetch`
Add dependency to build.zig.zon.

```typescript
interface ZigFetchArgs {
  url: string;          // Package URL or name
  cwd: string;
}

// Runs: zig fetch --save <url>
// Returns: { success, hash, stdout, stderr }
```

### Existing Tools (Unchanged)
- `zig_build` - Build with structured errors
- `zig_test` - Run tests with counts
- `zig_check` - Fast syntax/type check
- `zig_fmt` - Format code
- `zig_version` - Check Zig version
- `zig_init` - Initialize project
- `zig_translate_c` - Convert C headers

---

## Commands

### `/zig-setup`
First-time toolchain setup.

**Flow:**
1. Check if ZVM installed → guide installation if not
2. Install master Zig + ZLS via `zvm i master --zls`
3. Detect Zed → offer to configure `~/.zvm/bin/zls` path
4. Verify with `zig version` + `zls --version`
5. Report success with next steps

### `/zig-update`
Update nightly toolchain.

**Flow:**
1. Run `zvm i master --zls -f` (force reinstall latest)
2. Verify versions match after update
3. Report: old version → new version

### `/zig-doctor`
Diagnose toolchain health.

**Checks:**
- ZVM installed and in PATH?
- Zig installed and working?
- ZLS installed?
- ZLS version matches Zig version?
- Zed configured correctly? (if Zed detected)
- build.zig exists and parses? (if in project)

**Output:** Clear pass/fail with fix commands for each failure.

### `/zig-new <name> [type]`
Create new project.

**Types:**
- `exe` (default) - Executable with main()
- `lib` - Library
- `c-lib` - C-compatible library

**Flow:**
1. Create directory
2. Run `zig init`
3. Apply template overlay (GPA setup, error handling for exe)
4. Initialize git repo
5. Report created files

### `/zig-add <package>`
Add dependency.

**Supported formats:**
- Full URL: `https://github.com/owner/repo/archive/ref.tar.gz`
- GitHub shorthand: `owner/repo` or `owner/repo@tag`
- Package name: (future - zigistry lookup)

**Flow:**
1. Resolve URL from input
2. Run `zig fetch --save <url>`
3. Show how to import in build.zig

---

## AI Agent Optimizations

### Proactive Health Checks

Add to SKILL.md trigger behavior:

```markdown
## Auto-Checks (Before Any Zig Task)

When working in a Zig project, automatically verify:
- `zig version` succeeds
- ZLS responds (if editing in Zed)
- build.zig exists and parses

If any fail, run /zig-doctor before proceeding.
```

### Structured Error Parsing

Enhance MCP error parsing to include:
- **Error chains** - Zig's "note: called from here" traces
- **Fix suggestions** - Common errors with known fixes
- **Related errors** - Group errors from same root cause

### Fast Feedback Loop

Priority order for TDD:
1. `zig_check` (ast-check) - milliseconds, syntax only
2. `zig build` - seconds, full type checking
3. `zig_test --filter=<name>` - run specific test

### Context Awareness

Patterns Claude should recognize:
- Allocator leaks → suggest defer/errdefer
- Comptime errors → explain what can't be runtime
- C interop issues → suggest translate-c workflow

---

## Hooks

### format-on-edit.json (Optional)

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "command": "if [[ \"$TOOL_INPUT\" == *\".zig\"* ]]; then zig fmt \"$FILE_PATH\" 2>/dev/null; fi"
    }]
  }
}
```

Auto-formats .zig files after Claude edits them.

### Pre-Commit Check (Optional)

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash:git commit",
      "command": "zig build 2>&1 || echo 'Warning: build has errors'"
    }]
  }
}
```

### Not Needed

- **Linting hook**: Zig compiler is the linter
- **Doc generation hook**: Manual when needed
- **ZLS hook**: Zed handles directly

---

## Templates

### .zed/settings.json

For projects using ZVM-managed ZLS:

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

---

## Reference Documents

### references/zvm.md (~150 lines)
- Installation methods
- PATH configuration
- Version management commands
- Troubleshooting (permissions, PATH conflicts)

### references/zls.md (~100 lines)
- How ZLS versions work
- Manual installation (edge cases)
- Common errors and fixes
- Configuration options

### references/zed-integration.md (~80 lines)
- Zed + ZVM + ZLS setup
- Settings configuration
- "Version mismatch" troubleshooting
- Tips for nightly users

---

## Implementation Order

1. **MCP Tools** - Foundation for everything else
2. **Commands** - User-facing layer
3. **References & SKILL.md updates** - Documentation
4. **Templates & Hooks** - Conveniences
5. **install.sh update** - ZVM detection and guidance

---

## Success Criteria

- [ ] `/zig-setup` gets new user from zero to working in <5 minutes
- [ ] `/zig-doctor` clearly diagnoses any toolchain issue
- [ ] Claude can autonomously fix ZLS version mismatches
- [ ] Tight TDD loop with `zig_check` + `zig_test`
- [ ] All existing tests still pass
- [ ] New MCP tools have test coverage
