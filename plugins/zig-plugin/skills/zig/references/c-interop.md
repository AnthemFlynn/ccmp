# C Interoperability Deep Dive

Zig has first-class C interoperability. You can call C code from Zig and call Zig from C without any FFI overhead.

## Importing C Code

### @cImport - Direct Header Import

```zig
const c = @cImport({
    @cDefine("_GNU_SOURCE", {});
    @cInclude("stdio.h");
    @cInclude("stdlib.h");
});

pub fn main() void {
    _ = c.printf("Hello from Zig!\n");
}
```

**@cImport directives:**
- `@cInclude("header.h")` - Include a C header
- `@cDefine("NAME", value)` - Define preprocessor macro
- `@cUndef("NAME")` - Undefine a macro

### translate-c - Manual Translation

For more control, use the translate-c command:

```bash
zig translate-c myheader.h > c_bindings.zig
```

With include paths and defines:
```bash
zig translate-c -I/usr/include -DDEBUG=1 myheader.h
```

**When to use translate-c vs @cImport:**
- `@cImport`: Quick prototyping, small headers, automatic updates
- `translate-c`: Large libraries, need to customize bindings, faster compile times

## Calling C Functions

### Basic Calls

```zig
const c = @cImport(@cInclude("math.h"));

pub fn main() void {
    const result = c.sqrt(16.0);  // Returns 4.0
    _ = c.printf("sqrt(16) = %f\n", result);
}
```

### Handling C Pointers

```zig
const c = @cImport(@cInclude("string.h"));

pub fn main() void {
    var buffer: [100]u8 = undefined;
    
    // C functions that take char* work with [*c]u8
    _ = c.strcpy(&buffer, "Hello");
    
    // Convert to Zig slice for safe operations
    const len = c.strlen(&buffer);
    const slice: []u8 = buffer[0..len];
    
    std.debug.print("String: {s}\n", .{slice});
}
```

### Pointer Type Conversions

```zig
// C pointer types in Zig
[*c]T        // C pointer (nullable, arithmetic allowed)
*T           // Single-item pointer (non-null)
[*]T         // Many-item pointer (non-null)
?*T          // Optional single-item pointer

// Conversions
const c_ptr: [*c]u8 = &buffer;
const zig_ptr: *u8 = c_ptr;  // Implicit if non-null guaranteed
const opt_ptr: ?*u8 = c_ptr; // Always safe

// From Zig to C
const zig_slice: []u8 = &buffer;
const c_ptr2: [*c]u8 = zig_slice.ptr;
```

## Exposing Zig to C

### Export Functions

```zig
// Callable from C as: int add(int a, int b);
export fn add(a: c_int, b: c_int) c_int {
    return a + b;
}

// With custom name
export fn zigFunction() void {}
comptime {
    @export(zigFunction, .{ .name = "my_c_function" });
}
```

### Export Types

```zig
// C-compatible struct layout
pub const MyStruct = extern struct {
    x: c_int,
    y: c_int,
    name: [*c]const u8,
};

// Packed struct (no padding)
pub const PackedData = packed struct {
    flags: u8,
    id: u16,
    value: u32,
};
```

### Creating a C Library from Zig

```zig
// lib.zig
const std = @import("std");

// Exported types
pub const Context = extern struct {
    data: ?*anyopaque,
    size: usize,
};

// Exported functions
export fn mylib_create() ?*Context {
    // Use C allocator for C interop
    const ctx = std.heap.c_allocator.create(Context) catch return null;
    ctx.* = .{ .data = null, .size = 0 };
    return ctx;
}

export fn mylib_destroy(ctx: ?*Context) void {
    if (ctx) |c| {
        std.heap.c_allocator.destroy(c);
    }
}

export fn mylib_process(ctx: *Context, input: [*c]const u8, len: usize) c_int {
    const slice = input[0..len];
    // Process...
    ctx.size = slice.len;
    return 0;
}
```

Build configuration:
```zig
// build.zig
const lib = b.addSharedLibrary(.{
    .name = "mylib",
    .root_source_file = b.path("src/lib.zig"),
    .target = target,
    .optimize = optimize,
});
lib.linkLibC();  // Required for c_allocator
b.installArtifact(lib);
```

## C Types in Zig

### Standard C Types

```zig
// Integer types (platform-dependent sizes)
c_short      // short
c_ushort     // unsigned short
c_int        // int
c_uint       // unsigned int
c_long       // long
c_ulong      // unsigned long
c_longlong   // long long
c_ulonglong  // unsigned long long

// Fixed-size (when C uses stdint.h)
i8, i16, i32, i64   // int8_t, int16_t, etc.
u8, u16, u32, u64   // uint8_t, uint16_t, etc.

// Other types
c_char       // char (may be signed or unsigned)
usize        // size_t
isize        // ptrdiff_t / ssize_t
```

### Struct Layout

```zig
// extern struct: C ABI compatible, may have padding
const CStruct = extern struct {
    a: u8,      // offset 0
    // 3 bytes padding
    b: u32,     // offset 4
    c: u8,      // offset 8
    // 3 bytes padding
};  // size: 12

// packed struct: no padding, may be unaligned
const PackedStruct = packed struct {
    a: u8,      // offset 0
    b: u32,     // offset 1 (unaligned!)
    c: u8,      // offset 5
};  // size: 6
```

### Unions

```zig
// C-compatible union
const CUnion = extern union {
    as_int: c_int,
    as_float: f32,
    as_bytes: [4]u8,
};

// Tagged union (not C-compatible)
const ZigUnion = union(enum) {
    int_val: i32,
    float_val: f32,
};
```

## Memory Management Patterns

### Who Owns What?

```zig
// Pattern 1: Zig allocates, Zig frees
pub fn createBuffer(allocator: Allocator) ![]u8 {
    return allocator.alloc(u8, 1024);
}

// Pattern 2: C allocates, Zig wraps
pub fn wrapCString(c_str: [*c]const u8) []const u8 {
    if (c_str == null) return "";
    return std.mem.span(c_str);
}

// Pattern 3: Zig allocates for C (use c_allocator)
export fn create_data() ?[*]u8 {
    return std.heap.c_allocator.alloc(u8, 1024) catch null;
}

export fn free_data(ptr: ?[*]u8, len: usize) void {
    if (ptr) |p| {
        std.heap.c_allocator.free(p[0..len]);
    }
}
```

### String Handling

```zig
// C string (null-terminated) to Zig slice
fn cStringToSlice(c_str: [*c]const u8) []const u8 {
    return std.mem.span(c_str);
}

// Zig slice to C string (must ensure null termination)
fn sliceToCString(allocator: Allocator, slice: []const u8) ![*:0]u8 {
    return allocator.dupeZ(u8, slice);
}

// Using sentinel-terminated arrays
const hello: [:0]const u8 = "Hello";  // Compile-time null-terminated
const c_hello: [*c]const u8 = hello;  // Can pass to C
```

## Building C Code with Zig

### Linking System Libraries

```zig
// build.zig
exe.linkSystemLibrary("sqlite3");
exe.linkSystemLibrary("ssl");
exe.linkSystemLibrary("crypto");
exe.linkLibC();
```

### Compiling C Sources

```zig
// build.zig
exe.addCSourceFiles(.{
    .files = &.{
        "vendor/sqlite3.c",
        "vendor/lz4.c",
    },
    .flags = &.{
        "-std=c99",
        "-O2",
        "-DSQLITE_ENABLE_FTS5",
    },
});
exe.addIncludePath(b.path("vendor"));
exe.linkLibC();
```

### Cross-Compiling C Code

Zig can cross-compile C code to any target:

```zig
// build.zig
pub fn build(b: *std.Build) void {
    // Target ARM Linux
    const target = b.resolveTargetQuery(.{
        .cpu_arch = .aarch64,
        .os_tag = .linux,
        .abi = .gnu,
    });
    
    const exe = b.addExecutable(.{
        .name = "app",
        .root_source_file = b.path("src/main.zig"),
        .target = target,
    });
    
    // C code will be cross-compiled too
    exe.addCSourceFile(.{
        .file = b.path("vendor/lib.c"),
        .flags = &.{},
    });
    exe.linkLibC();  // Uses Zig's bundled libc
}
```

## Common Patterns

### Wrapping a C Library

```zig
// Low-level bindings
const c = @cImport(@cInclude("mylib.h"));

// High-level Zig wrapper
pub const Context = struct {
    handle: *c.mylib_ctx,
    allocator: Allocator,

    pub fn init(allocator: Allocator) !Context {
        const h = c.mylib_create() orelse return error.InitFailed;
        return .{ .handle = h, .allocator = allocator };
    }

    pub fn deinit(self: Context) void {
        c.mylib_destroy(self.handle);
    }

    pub fn process(self: *Context, data: []const u8) ![]u8 {
        var out_len: usize = 0;
        const result = c.mylib_process(self.handle, data.ptr, data.len, &out_len);
        if (result != 0) return error.ProcessFailed;
        
        const output = try self.allocator.alloc(u8, out_len);
        @memcpy(output, c.mylib_get_output(self.handle)[0..out_len]);
        return output;
    }
};
```

### Callbacks

```zig
// C callback type: void (*callback)(void* user_data, int result)

const Callback = struct {
    context: *anyopaque,
    func: *const fn (*anyopaque, c_int) void,
};

export fn register_callback(
    ctx: *anyopaque,
    func: *const fn (*anyopaque, c_int) callconv(.C) void,
) void {
    // Store and use callback
    func(ctx, 42);
}

// Zig side
fn myCallback(ctx: *anyopaque, result: c_int) callconv(.C) void {
    const data: *MyData = @ptrCast(@alignCast(ctx));
    data.handleResult(result);
}
```

## Gotchas

### Null Pointers

```zig
// [*c] can be null, * cannot
fn process(ptr: [*c]u8) void {
    if (ptr == null) return;  // Must check!
    
    // Or convert with null check
    const safe: *u8 = ptr orelse return;
    _ = safe;
}
```

### Alignment

```zig
// C code may return unaligned pointers
// Use @alignCast carefully
const aligned: *align(4) u32 = @alignCast(c_ptr);
```

### Calling Convention

```zig
// For callbacks passed to C, must use callconv(.C)
fn zigCallback(arg: c_int) callconv(.C) c_int {
    return arg * 2;
}
```
