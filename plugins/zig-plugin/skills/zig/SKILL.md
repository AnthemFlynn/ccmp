---
name: zig
description: >
  Comprehensive Zig development support with deep understanding of allocators, comptime, error unions, 
  build.zig patterns, and C interoperability. Use this skill for any Zig programming task including:
  (1) Writing new Zig code with proper allocator patterns, (2) Debugging allocator and memory issues,
  (3) Comptime metaprogramming and generic data structures, (4) build.zig configuration and cross-compilation,
  (5) C library wrapping and FFI, (6) Error handling with error unions and errdefer, (7) Testing with 
  Zig's built-in test framework. Triggers on: .zig files, build.zig, build.zig.zon, zig commands, 
  mentions of allocators, comptime, or Zig-specific concepts.
---

# Zig Development Skill

Zig is a systems programming language emphasizing explicit memory management, compile-time evaluation, and C interoperability. This skill enables effective Zig development by encoding patterns that LLMs commonly get wrong.

## Core Philosophy

Zig's design principles that must inform all code generation:

1. **No hidden control flow** - No operator overloading, no hidden allocations
2. **No hidden memory allocations** - Allocators are explicit parameters
3. **Explicit is better than implicit** - Side effects are visible at call sites
4. **Errors are values** - Error unions, not exceptions
5. **Comptime over runtime** - Move work to compile time when possible

## Toolchain Management

### Version Strategy

- Use `master` (nightly) for latest features until Zig 1.0
- ZLS must match Zig version exactly (nightly↔nightly, tagged↔tagged)
- ZVM's `--zls` flag keeps them in sync automatically

### Common Operations

```bash
# First-time setup
zvm i master --zls

# Update to latest nightly
zvm i master --zls -f

# Switch versions
zvm use 0.13.0

# Check health
/zig-doctor
```

### Auto-Checks (Before Any Zig Task)

When working in a Zig project, automatically verify:
- `zig version` succeeds
- ZLS responds (if editing in Zed)
- build.zig exists and parses

If any fail, run `/zig-doctor` before proceeding.

## Quick Reference

### Project Structure

```
project/
├── build.zig          # Build configuration (Zig code)
├── build.zig.zon      # Package manifest (declarative)
├── src/
│   ├── main.zig       # Application entry point
│   ├── lib.zig        # Library root (if applicable)
│   └── module/        # Submodules
└── test/              # Integration tests (unit tests in src/)
```

### Allocator Selection Decision Tree

```
Is this a short-lived operation with bounded size?
├─ Yes: ArenaAllocator (bulk free, fast alloc)
├─ No: Is this for debugging/development?
│   ├─ Yes: GeneralPurposeAllocator (leak detection, use-after-free detection)
│   └─ No: Is memory size known at compile time?
│       ├─ Yes: FixedBufferAllocator (zero heap, embedded-friendly)
│       └─ No: Is this performance-critical production code?
│           ├─ Yes: c_allocator or page_allocator (system allocator)
│           └─ No: GeneralPurposeAllocator with safety checks
```

### Error Handling Patterns

```zig
// Returning errors - use error union
fn riskyOperation(allocator: Allocator) !Result {
    const data = try allocator.alloc(u8, size);  // propagate error
    errdefer allocator.free(data);               // cleanup on error
    
    return processData(data) catch |err| {
        log.err("Processing failed: {}", .{err});
        return error.ProcessingFailed;
    };
}

// Optional values - use ?T, not sentinel
fn findItem(items: []const Item, key: u32) ?*const Item {
    for (items) |*item| {
        if (item.key == key) return item;
    }
    return null;
}
```

### Comptime Fundamentals

```zig
// Type-level programming
fn GenericList(comptime T: type) type {
    return struct {
        items: []T,
        allocator: Allocator,
        
        const Self = @This();
        
        pub fn init(allocator: Allocator) Self {
            return .{ .items = &.{}, .allocator = allocator };
        }
    };
}

// Compile-time string processing
fn comptimeHash(comptime str: []const u8) u32 {
    comptime {
        var hash: u32 = 0;
        for (str) |c| hash = hash *% 31 +% c;
        return hash;
    }
}
```

## Common Anti-Patterns to Avoid

### Memory Management

❌ **Wrong**: Allocating without considering ownership
```zig
fn badPattern() []u8 {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    return gpa.allocator().alloc(u8, 100) catch unreachable;
    // gpa goes out of scope, allocator invalidated!
}
```

✅ **Correct**: Allocator passed as parameter
```zig
fn goodPattern(allocator: Allocator) ![]u8 {
    return allocator.alloc(u8, 100);
}
```

### Error Handling

❌ **Wrong**: Using `catch unreachable` for recoverable errors
```zig
const file = std.fs.cwd().openFile(path, .{}) catch unreachable;
```

✅ **Correct**: Propagate or handle explicitly
```zig
const file = std.fs.cwd().openFile(path, .{}) catch |err| {
    return switch (err) {
        error.FileNotFound => error.ConfigMissing,
        else => err,
    };
};
```

### Comptime

❌ **Wrong**: Runtime operations in comptime context
```zig
fn badComptime(runtime_val: usize) type {
    // runtime_val is not comptime-known!
    return [runtime_val]u8;
}
```

✅ **Correct**: Comptime parameter or inline
```zig
fn goodComptime(comptime size: usize) type {
    return [size]u8;
}

// Or use slices for runtime-sized arrays
fn runtimeSized(allocator: Allocator, size: usize) ![]u8 {
    return allocator.alloc(u8, size);
}
```

## Resources

Detailed guidance available in reference files:

### Core Concepts
- **[references/allocators.md](references/allocators.md)**: Deep dive on allocator patterns, arena strategies, custom allocators
- **[references/comptime.md](references/comptime.md)**: Type-level programming, @typeInfo, @Type, comptime algorithms
- **[references/build-system.md](references/build-system.md)**: build.zig mastery, cross-compilation, C integration
- **[references/error-handling.md](references/error-handling.md)**: Error sets, errdefer, error traces, panic handling
- **[references/c-interop.md](references/c-interop.md)**: translate-c, C types, calling conventions, building C code
- **[references/testing.md](references/testing.md)**: Test blocks, expect, fuzz testing, test allocator

### Toolchain & Editor
- **[references/zvm.md](references/zvm.md)**: ZVM installation, version management, troubleshooting
- **[references/zls.md](references/zls.md)**: ZLS configuration, editor integration, diagnostics
- **[references/zed-integration.md](references/zed-integration.md)**: Zed-specific setup for ZVM-managed ZLS

## Templates

Project scaffolding for common patterns:

- **[templates/cli-app](../../templates/cli-app/)** - Command-line application with argument parsing, GPA leak detection, proper error handling
- **[templates/library](../../templates/library/)** - Reusable library with tests and documentation structure

Copy and customize for new projects:

```bash
cp -r templates/cli-app my-new-app
cd my-new-app
# Edit build.zig to rename "myapp" to your project name
zig build run
```

## MCP Server Integration

When the `zig-mcp` MCP server is available, use these tools:

### Build Tools
- `zig_build` - Run `zig build` with optional target/step, returns structured errors with file/line/column
- `zig_test` - Run `zig build test`, returns pass/fail/skip counts and any compile errors
- `zig_check` - Fast syntax/type checking without full build (uses ast-check for single files)
- `zig_fmt` - Format code or check formatting, returns list of affected files

### Project Tools
- `zig_version` - Check if Zig is installed, get version with parsed components
- `zig_init` - Initialize a new Zig project with standard structure
- `zig_fetch` - Add dependency to build.zig.zon using `zig fetch --save`
- `zig_translate_c` - Convert C headers to Zig declarations

### Toolchain Tools (ZVM/ZLS)
- `zvm_install` - Install Zig version with optional matching ZLS
- `zvm_use` - Switch active Zig version
- `zvm_list` - List installed versions and show active
- `zls_status` - Check ZLS installation and version compatibility

## Workflow Integration

For multi-step development workflows, see:

- **TDD Loop**: `workflows/tdd-loop.md` - Red-green-refactor with zig test
- **C Wrapper**: `workflows/c-wrapper.md` - Systematic C library wrapping
