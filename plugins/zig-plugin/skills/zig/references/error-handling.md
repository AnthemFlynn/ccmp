# Error Handling Deep Dive

Zig's error handling uses error unions - values that are either a success value or an error. This is distinct from exceptions, Result types, or errno patterns.

## Error Union Fundamentals

### Basic Syntax

```zig
// Function that can fail
fn divide(a: i32, b: i32) !i32 {
    if (b == 0) return error.DivisionByZero;
    return @divTrunc(a, b);
}

// Using the function
pub fn main() !void {
    const result = try divide(10, 2);  // Propagates error if any
    std.debug.print("Result: {}\n", .{result});
}
```

### Error Sets

```zig
// Explicit error set
const MathError = error{
    DivisionByZero,
    Overflow,
    Underflow,
};

fn safeDivide(a: i32, b: i32) MathError!i32 {
    if (b == 0) return error.DivisionByZero;
    return @divTrunc(a, b);
}

// Inferred error set (anyerror)
fn riskyOperation() !void {
    // Error set inferred from all possible errors
}
```

## Error Handling Patterns

### try - Propagate Errors

```zig
fn processFile(path: []const u8) !Data {
    const file = try std.fs.cwd().openFile(path, .{});
    defer file.close();
    
    const content = try file.readToEndAlloc(allocator, max_size);
    defer allocator.free(content);
    
    return try parseData(content);
}
```

### catch - Handle Errors

```zig
// Provide default value
const value = getValue() catch 0;

// Handle specific errors
const file = openFile(path) catch |err| switch (err) {
    error.FileNotFound => {
        std.log.warn("File not found, using defaults", .{});
        return defaults;
    },
    error.AccessDenied => return error.PermissionError,
    else => return err,
};

// Log and re-throw
const data = parse(input) catch |err| {
    std.log.err("Parse failed: {}", .{err});
    return err;
};
```

### if-else with Error Unions

```zig
if (riskyOperation()) |value| {
    // Success path
    process(value);
} else |err| {
    // Error path
    handleError(err);
}
```

## errdefer - Cleanup on Error

The killer feature for resource management:

```zig
fn createResource(allocator: Allocator) !*Resource {
    const memory = try allocator.alloc(u8, 1024);
    errdefer allocator.free(memory);  // Only runs if function returns error
    
    const handle = try openHandle();
    errdefer closeHandle(handle);  // Cleanup in reverse order
    
    try validateHandle(handle);  // If this fails, both errdefers run
    
    return Resource{ .memory = memory, .handle = handle };
}
```

### errdefer vs defer

```zig
fn example(allocator: Allocator) !Result {
    const a = try allocator.alloc(u8, 100);
    errdefer allocator.free(a);  // Only on error return
    
    const b = try allocator.alloc(u8, 100);
    errdefer allocator.free(b);
    
    // If we reach here, both allocations succeeded
    // errdefers won't run, caller owns both allocations
    return Result{ .a = a, .b = b };
}

fn exampleWithDefer(allocator: Allocator) !void {
    const temp = try allocator.alloc(u8, 100);
    defer allocator.free(temp);  // Always runs when scope exits
    
    try processData(temp);
    // defer runs here, whether success or error
}
```

### errdefer with Capture

```zig
fn multiStepOperation(allocator: Allocator) !Result {
    var state = try initState(allocator);
    errdefer |err| {
        std.log.err("Operation failed at step {}: {}", .{state.step, err});
        state.deinit();
    };
    
    try state.step1();
    try state.step2();
    try state.step3();
    
    return state.finalize();
}
```

## Error Traces

Zig provides stack traces for errors in debug builds:

```zig
fn level3() !void {
    return error.SomethingWentWrong;
}

fn level2() !void {
    try level3();
}

fn level1() !void {
    try level2();
}

pub fn main() void {
    level1() catch |err| {
        std.debug.print("Error: {}\n", .{err});
        if (@errorReturnTrace()) |trace| {
            std.debug.dumpStackTrace(trace.*);
        }
    };
}
```

## Error Coercion and Merging

### Widening Error Sets

```zig
const FileError = error{ NotFound, AccessDenied };
const ParseError = error{ InvalidFormat, UnexpectedToken };

// Function can return either error set
fn processFile(path: []const u8) (FileError || ParseError)!Data {
    const content = openAndRead(path) catch |err| return err;  // FileError
    return parse(content);  // ParseError
}
```

### Narrowing with switch

```zig
fn handleError(err: anyerror) void {
    switch (err) {
        error.OutOfMemory => @panic("OOM"),
        error.FileNotFound => std.log.warn("File missing", .{}),
        else => std.log.err("Unknown error: {}", .{err}),
    }
}
```

## Optional vs Error Union

```zig
// Use optional when absence is not an error
fn find(items: []const Item, key: u32) ?*const Item {
    for (items) |*item| {
        if (item.key == key) return item;
    }
    return null;  // Not found is expected, not an error
}

// Use error union when failure needs explanation
fn load(path: []const u8) !Data {
    const file = std.fs.cwd().openFile(path, .{}) catch |err| {
        return switch (err) {
            error.FileNotFound => error.ConfigMissing,
            error.AccessDenied => error.PermissionDenied,
            else => error.LoadFailed,
        };
    };
    // ...
}
```

## Patterns for Error Context

### Wrapping Errors with Context

```zig
const ContextualError = struct {
    err: anyerror,
    context: []const u8,
    
    pub fn format(self: @This(), comptime fmt: []const u8, options: std.fmt.FormatOptions, writer: anytype) !void {
        _ = fmt;
        _ = options;
        try writer.print("{s}: {}", .{ self.context, self.err });
    }
};

fn withContext(err: anyerror, context: []const u8) ContextualError {
    return .{ .err = err, .context = context };
}
```

### Error Payloads (Zig 0.12+)

```zig
// Future Zig versions will support error payloads
// For now, use out-parameters or wrapper types
fn parseWithDetails(input: []const u8, error_info: *ErrorInfo) !Ast {
    // ...
    if (invalid) {
        error_info.* = .{
            .line = line,
            .column = column,
            .message = "unexpected token",
        };
        return error.ParseError;
    }
}
```

## Testing Error Paths

```zig
const testing = std.testing;

test "divide by zero returns error" {
    try testing.expectError(error.DivisionByZero, divide(10, 0));
}

test "valid division succeeds" {
    const result = try divide(10, 2);
    try testing.expectEqual(@as(i32, 5), result);
}

test "error propagation" {
    const S = struct {
        fn inner() !i32 {
            return error.TestError;
        }
        fn outer() !i32 {
            return try inner();
        }
    };
    
    try testing.expectError(error.TestError, S.outer());
}
```

## Common Anti-Patterns

### ❌ Using catch unreachable for recoverable errors

```zig
// BAD: Crashes on any file error
const file = std.fs.cwd().openFile(path, .{}) catch unreachable;
```

### ✅ Handle or propagate

```zig
// GOOD: Propagate to caller
const file = try std.fs.cwd().openFile(path, .{});

// GOOD: Handle with fallback
const file = std.fs.cwd().openFile(path, .{}) catch |err| {
    std.log.warn("Could not open {s}: {}", .{path, err});
    return getDefaultConfig();
};
```

### ❌ Ignoring errors silently

```zig
// BAD: Error is lost
_ = riskyOperation() catch {};
```

### ✅ At minimum, log errors

```zig
// GOOD: Error is visible
riskyOperation() catch |err| {
    std.log.err("Operation failed: {}", .{err});
};
```

### ❌ Overly broad error handling

```zig
// BAD: All errors treated the same
doSomething() catch return error.Failed;
```

### ✅ Preserve error information

```zig
// GOOD: Specific handling, preserve unknown errors
doSomething() catch |err| switch (err) {
    error.Timeout => return error.NetworkTimeout,
    error.ConnectionRefused => return error.ServiceUnavailable,
    else => return err,  // Preserve original error
};
```
