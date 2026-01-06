# C Library Wrapping Workflow

Systematic approach to creating Zig bindings for C libraries.

## Overview

This workflow guides the process of wrapping a C library for idiomatic Zig usage:

1. Analyze the C API
2. Generate raw bindings with translate-c
3. Create a Zig-idiomatic wrapper layer
4. Set up build integration
5. Test the bindings

## The Process

```
┌─────────────────────────────────────────────────────────┐
│  1. ANALYZE: Understand the C API                       │
│     ↓                                                   │
│  2. TRANSLATE: Generate raw Zig bindings                │
│     ↓                                                   │
│  3. WRAP: Create idiomatic Zig interface                │
│     ↓                                                   │
│  4. BUILD: Configure build.zig                          │
│     ↓                                                   │
│  5. TEST: Verify functionality                          │
└─────────────────────────────────────────────────────────┘
```

## Step 1: Analyze the C API

### Using MCP Tools

```
→ zig_translate_c(header: "vendor/mylib.h", includes: ["vendor"])
```

Review the output to understand:
- What types are exposed
- What functions are available
- What #defines/macros exist
- Memory management patterns

### Key Questions

1. **Who allocates memory?**
   - Does the library allocate internally?
   - Does the caller provide buffers?
   - Are there cleanup functions?

2. **What's the error handling pattern?**
   - Return codes?
   - errno?
   - Out parameters?

3. **Is it thread-safe?**
   - Global state?
   - Thread-local storage?
   - Mutex requirements?

## Step 2: Generate Raw Bindings

### Option A: Direct @cImport (Simple Libraries)

```zig
// src/c.zig
pub const c = @cImport({
    @cInclude("mylib.h");
});
```

**Pros**: Simple, automatic updates when header changes
**Cons**: Compilation-time overhead, harder to customize

### Option B: translate-c + Manual Curation (Complex Libraries)

```
→ zig_translate_c(header: "mylib.h")
# Save the returned `zigCode` to src/c_bindings.zig
```

Then manually edit to:
- Remove unused declarations
- Fix any translation issues
- Add documentation

**Pros**: Full control, faster compilation
**Cons**: Manual maintenance when C API changes

### Common translate-c Fixes

```zig
// Original (problematic)
pub extern fn mylib_process(data: [*c]u8, len: c_int) c_int;

// Fixed (Zig-appropriate types)
pub extern fn mylib_process(data: [*]u8, len: usize) c_int;
```

## Step 3: Create Idiomatic Wrapper

### Basic Pattern

```zig
// src/mylib.zig
const c = @import("c.zig").c;
const std = @import("std");
const Allocator = std.mem.Allocator;

pub const Error = error{
    InitFailed,
    ProcessingError,
    OutOfMemory,
};

pub const Context = struct {
    handle: *c.mylib_ctx,
    allocator: Allocator,

    pub fn init(allocator: Allocator) Error!Context {
        const handle = c.mylib_init() orelse return error.InitFailed;
        return .{ .handle = handle, .allocator = allocator };
    }

    pub fn deinit(self: *Context) void {
        c.mylib_cleanup(self.handle);
    }

    pub fn process(self: *Context, input: []const u8) Error![]u8 {
        var out_len: usize = 0;
        const result = c.mylib_process(
            self.handle,
            input.ptr,
            input.len,
            &out_len,
        );
        
        if (result < 0) {
            return error.ProcessingError;
        }
        
        // Copy C-allocated data to Zig-managed memory
        const output = try self.allocator.alloc(u8, out_len);
        @memcpy(output, c.mylib_get_output(self.handle)[0..out_len]);
        return output;
    }
};
```

### Wrapper Patterns

#### Converting Return Codes to Errors

```zig
fn checkError(code: c_int) Error!void {
    return switch (code) {
        0 => {},
        -1 => error.InvalidArgument,
        -2 => error.OutOfMemory,
        -3 => error.IoError,
        else => error.Unknown,
    };
}

pub fn doSomething(self: *Self) Error!void {
    try checkError(c.mylib_do_something(self.handle));
}
```

#### Converting Nullable Pointers to Optionals

```zig
pub fn find(self: *Self, key: []const u8) ?*const Value {
    const result = c.mylib_find(self.handle, key.ptr, key.len);
    return if (result) |ptr| ptr else null;
}
```

#### Managing C Strings

```zig
pub fn getName(self: *Self, allocator: Allocator) ![]u8 {
    const c_str = c.mylib_get_name(self.handle);
    if (c_str == null) return error.NoName;
    
    const len = std.mem.len(c_str);
    const result = try allocator.alloc(u8, len);
    @memcpy(result, c_str[0..len]);
    return result;
}

pub fn setName(self: *Self, name: []const u8) !void {
    // Ensure null termination for C
    var buf: [256]u8 = undefined;
    if (name.len >= buf.len) return error.NameTooLong;
    
    @memcpy(buf[0..name.len], name);
    buf[name.len] = 0;
    
    try checkError(c.mylib_set_name(self.handle, &buf));
}
```

#### Callback Wrapping

```zig
// C callback signature
// typedef void (*mylib_callback)(void* user_data, int event, const char* message);

pub const Callback = *const fn (event: Event, message: []const u8) void;

pub fn setCallback(self: *Self, callback: Callback) void {
    // Store callback in struct for the C callback to access
    self.callback = callback;
    
    c.mylib_set_callback(self.handle, cCallback, self);
}

fn cCallback(user_data: ?*anyopaque, event: c_int, message: [*c]const u8) callconv(.C) void {
    const self: *Self = @ptrCast(@alignCast(user_data));
    const msg = std.mem.span(message);
    self.callback.?(@enumFromInt(event), msg);
}
```

## Step 4: Configure build.zig

```zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // The Zig module
    const mylib_mod = b.addModule("mylib", .{
        .root_source_file = b.path("src/mylib.zig"),
        .target = target,
        .optimize = optimize,
    });

    // Link the C library
    mylib_mod.linkSystemLibrary("mylib");
    mylib_mod.linkLibC();

    // Or build C sources directly
    // mylib_mod.addCSourceFiles(.{
    //     .files = &.{ "vendor/mylib.c" },
    //     .flags = &.{ "-DMYLIB_STATIC" },
    // });
    // mylib_mod.addIncludePath(b.path("vendor"));

    // Example executable using the wrapper
    const exe = b.addExecutable(.{
        .name = "example",
        .root_source_file = b.path("examples/main.zig"),
        .target = target,
        .optimize = optimize,
    });
    exe.root_module.addImport("mylib", mylib_mod);
    b.installArtifact(exe);

    // Tests
    const tests = b.addTest(.{
        .root_source_file = b.path("src/mylib.zig"),
        .target = target,
        .optimize = optimize,
    });
    tests.linkSystemLibrary("mylib");
    tests.linkLibC();

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_tests.step);
}
```

### Building Vendored C Code

```zig
pub fn build(b: *std.Build) void {
    const lib = b.addStaticLibrary(.{
        .name = "mylib",
        .target = target,
        .optimize = optimize,
    });

    lib.addCSourceFiles(.{
        .files = &.{
            "vendor/mylib/src/core.c",
            "vendor/mylib/src/utils.c",
        },
        .flags = &.{
            "-std=c99",
            "-DMYLIB_STATIC",
            "-fno-sanitize=undefined",  // If needed
        },
    });

    lib.addIncludePath(b.path("vendor/mylib/include"));
    lib.linkLibC();

    // Now the Zig code can link against this
    const mylib_mod = b.addModule("mylib", .{
        .root_source_file = b.path("src/mylib.zig"),
    });
    mylib_mod.linkLibrary(lib);
}
```

## Step 5: Test the Bindings

### Unit Tests

```zig
const std = @import("std");
const testing = std.testing;
const mylib = @import("mylib.zig");

test "init and cleanup" {
    var ctx = try mylib.Context.init(testing.allocator);
    defer ctx.deinit();
}

test "process data" {
    var ctx = try mylib.Context.init(testing.allocator);
    defer ctx.deinit();

    const result = try ctx.process("hello");
    defer testing.allocator.free(result);

    try testing.expectEqualStrings("HELLO", result);
}

test "handles invalid input" {
    var ctx = try mylib.Context.init(testing.allocator);
    defer ctx.deinit();

    try testing.expectError(error.InvalidInput, ctx.process(""));
}
```

### Integration Testing with MCP

```
# Build and run tests
→ zig_test(cwd: ".")

# Cross-compile test (verify it builds for target)
→ zig_build(cwd: ".", target: "aarch64-linux")

# Check if code is formatted
→ zig_fmt(cwd: ".", path: "src/", check: true)
```

## Common Issues and Solutions

### Issue: Undefined symbols at link time

**Symptom**: `undefined reference to 'mylib_init'`

**Solutions**:
1. Check library search path: `exe.addLibraryPath(...)`
2. Check library name: `exe.linkSystemLibrary("mylib")` vs `exe.linkSystemLibrary("libmylib")`
3. For static libs: ensure all dependencies are also linked

### Issue: Header not found

**Symptom**: `'mylib.h' file not found`

**Solutions**:
1. Add include path: `exe.addIncludePath(b.path("vendor/include"))`
2. Use @cInclude with full path

### Issue: ABI mismatch

**Symptom**: Crashes or wrong values when calling C functions

**Solutions**:
1. Check calling convention: use `callconv(.C)` for callbacks
2. Check struct layout: may need `extern struct` or `packed struct`
3. Verify pointer types match

### Issue: Memory corruption

**Symptom**: Crashes, wrong data, or allocator errors

**Solutions**:
1. Verify ownership semantics (who frees what?)
2. Check for buffer size mismatches
3. Ensure strings are null-terminated when C expects it
4. Use ArenaAllocator for C-library-lifetime allocations

## Example: SQLite Wrapper

A complete SQLite wrapper would provide a high-level Zig interface:

```zig
// High-level Zig interface
const db = try sqlite.Database.open("test.db");
defer db.close();

var stmt = try db.prepare("SELECT * FROM users WHERE id = ?");
defer stmt.finalize();

try stmt.bind(1, user_id);

while (try stmt.step()) |row| {
    const name = row.text(0);
    const email = row.text(1);
    // ...
}
```

This pattern - raw C bindings wrapped in an idiomatic Zig struct with proper error handling and memory management - applies to any C library.
