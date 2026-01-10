# Testing Deep Dive

Zig has a built-in test framework that integrates tightly with the compiler. Tests are first-class citizens, not an afterthought.

## Test Basics

### Defining Tests

```zig
const std = @import("std");
const testing = std.testing;

test "simple test" {
    const x = 1 + 1;
    try testing.expectEqual(@as(u32, 2), x);
}

test "another test" {
    try testing.expect(true);
}
```

### Running Tests

```bash
# Run all tests in a file
zig test src/main.zig

# Run tests through build system
zig build test

# Filter tests by name
zig build test -- --test-filter "allocator"

# Verbose output
zig build test -- --verbose
```

## Assertions and Expectations

### Basic Expectations

```zig
const testing = std.testing;

test "expectations" {
    // Boolean assertion
    try testing.expect(1 + 1 == 2);
    
    // Equality (note: need explicit type for comptime values)
    try testing.expectEqual(@as(i32, 42), getValue());
    
    // Approximate equality for floats
    try testing.expectApproxEqAbs(@as(f32, 3.14159), pi, 0.0001);
    try testing.expectApproxEqRel(@as(f64, 1.0), computed, 0.01);
    
    // String equality
    try testing.expectEqualStrings("hello", greeting);
    
    // Slice equality
    try testing.expectEqualSlices(u8, &[_]u8{1, 2, 3}, slice);
    
    // Deep equality (for complex types)
    try testing.expectEqualDeep(expected_struct, actual_struct);
}
```

### Error Expectations

```zig
test "error expectations" {
    // Expect specific error
    try testing.expectError(error.InvalidInput, parse(""));
    
    // Expect any error
    const result = parse("");
    try testing.expect(result == error.InvalidInput);
}
```

### Format Checks

```zig
test "formatted output" {
    var buf: [100]u8 = undefined;
    const result = std.fmt.bufPrint(&buf, "{d}", .{42}) catch unreachable;
    try testing.expectEqualStrings("42", result);
    
    // Using expectFmt
    try testing.expectFmt("42", "{d}", .{42});
}
```

## Testing Allocator

The testing allocator is crucial for memory safety testing:

```zig
test "no memory leaks" {
    var list = std.ArrayList(u8).init(testing.allocator);
    defer list.deinit();  // Forgetting this fails the test!
    
    try list.append(1);
    try list.append(2);
    
    try testing.expectEqual(@as(usize, 2), list.items.len);
}
// Test automatically fails if any allocation wasn't freed
```

### What Testing Allocator Catches

```zig
test "leak detection" {
    const ptr = try testing.allocator.alloc(u8, 100);
    // Forgot to free - TEST FAILS with leak report
    _ = ptr;
}

test "double free detection" {
    const ptr = try testing.allocator.alloc(u8, 100);
    testing.allocator.free(ptr);
    // testing.allocator.free(ptr);  // Would crash: double free
}

test "use after free detection" {
    const ptr = try testing.allocator.alloc(u8, 100);
    testing.allocator.free(ptr);
    // ptr[0] = 42;  // Would crash: use after free
}
```

## Failing Allocator

Test allocation failure handling:

```zig
test "handles out of memory" {
    var failing = testing.FailingAllocator.init(testing.allocator, .{
        .fail_index = 0,  // Fail on first allocation
    });
    
    const result = MyStruct.init(failing.allocator());
    try testing.expectError(error.OutOfMemory, result);
}

test "handles partial allocation failure" {
    var failing = testing.FailingAllocator.init(testing.allocator, .{
        .fail_index = 2,  // Succeed twice, then fail
    });
    
    const allocator = failing.allocator();
    
    // These succeed
    const a = try allocator.alloc(u8, 10);
    defer allocator.free(a);
    const b = try allocator.alloc(u8, 10);
    defer allocator.free(b);
    
    // This fails
    try testing.expectError(error.OutOfMemory, allocator.alloc(u8, 10));
}
```

## Test Organization

### In-File Tests

```zig
// src/parser.zig

pub fn parse(input: []const u8) !Ast {
    // implementation
}

// Tests live with the code they test
test "parse empty" {
    const ast = try parse("");
    try testing.expect(ast.nodes.len == 0);
}

test "parse identifier" {
    const ast = try parse("foo");
    try testing.expectEqual(@as(usize, 1), ast.nodes.len);
}
```

### Test Namespaces

```zig
// Group related tests
const Parser = struct {
    // implementation
    
    test "Parser.init" {
        var p = Parser.init(testing.allocator);
        defer p.deinit();
    }
    
    test "Parser.parse basic" {
        var p = Parser.init(testing.allocator);
        defer p.deinit();
        _ = try p.parse("test");
    }
};

// Tests can reference the namespace
test "Parser usage" {
    _ = Parser;  // Run Parser's tests
}
```

### Separate Test Files

```zig
// tests/integration_test.zig
const std = @import("std");
const testing = std.testing;

// Import the module under test
const parser = @import("../src/parser.zig");
const compiler = @import("../src/compiler.zig");

test "full pipeline" {
    const source = "1 + 2";
    const ast = try parser.parse(testing.allocator, source);
    defer ast.deinit();
    
    const code = try compiler.compile(testing.allocator, ast);
    defer testing.allocator.free(code);
    
    try testing.expect(code.len > 0);
}
```

## Test Helpers

### Custom Test Functions

```zig
fn expectValidJson(input: []const u8) !void {
    const parsed = std.json.parseFromSlice(
        std.json.Value,
        testing.allocator,
        input,
        .{},
    ) catch |err| {
        std.debug.print("Invalid JSON: {s}\nError: {}\n", .{input, err});
        return error.InvalidJson;
    };
    defer parsed.deinit();
}

test "json validation" {
    try expectValidJson("{}");
    try expectValidJson("[1, 2, 3]");
    try testing.expectError(error.InvalidJson, expectValidJson("{invalid}"));
}
```

### Test Fixtures

```zig
const TestContext = struct {
    allocator: std.mem.Allocator,
    temp_dir: std.fs.Dir,
    
    fn init() !TestContext {
        const temp = try std.fs.cwd().makeOpenPath("test_temp", .{});
        return .{
            .allocator = testing.allocator,
            .temp_dir = temp,
        };
    }
    
    fn deinit(self: *TestContext) void {
        self.temp_dir.close();
        std.fs.cwd().deleteTree("test_temp") catch {};
    }
    
    fn createTestFile(self: *TestContext, name: []const u8, content: []const u8) !void {
        const file = try self.temp_dir.createFile(name, .{});
        defer file.close();
        try file.writeAll(content);
    }
};

test "file operations" {
    var ctx = try TestContext.init();
    defer ctx.deinit();
    
    try ctx.createTestFile("test.txt", "hello");
    // ... test file operations
}
```

## Parameterized Tests

```zig
test "addition properties" {
    const test_cases = [_]struct { a: i32, b: i32, expected: i32 }{
        .{ .a = 1, .b = 2, .expected = 3 },
        .{ .a = -1, .b = 1, .expected = 0 },
        .{ .a = 0, .b = 0, .expected = 0 },
        .{ .a = 100, .b = -100, .expected = 0 },
    };
    
    for (test_cases) |tc| {
        try testing.expectEqual(tc.expected, tc.a + tc.b);
    }
}
```

### Inline For for Compile-Time Test Generation

```zig
test "multiple types" {
    inline for ([_]type{ u8, u16, u32, u64 }) |T| {
        const max = std.math.maxInt(T);
        try testing.expect(max > 0);
    }
}
```

## Fuzz Testing

Zig supports built-in fuzz testing:

```zig
test "fuzz parser" {
    // This test will be run with many random inputs
    try std.testing.fuzz(.{}, fuzzer);
}

fn fuzzer(input: []const u8) !void {
    // Parser should never crash, regardless of input
    _ = parse(input) catch return;
}
```

Run with:
```bash
zig build test -- --fuzz
```

## Debugging Tests

### Print Debugging

```zig
test "with debug output" {
    const value = compute();
    std.debug.print("Computed: {}\n", .{value});  // Only shows on failure
    try testing.expectEqual(@as(i32, 42), value);
}
```

### Logging

```zig
test "with logging" {
    std.testing.log_level = .debug;
    
    std.log.debug("Starting test", .{});
    const result = performOperation();
    std.log.debug("Result: {}", .{result});
    
    try testing.expect(result.success);
}
```

## Build System Integration

### build.zig Test Configuration

```zig
pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // Unit tests
    const unit_tests = b.addTest(.{
        .root_source_file = b.path("src/lib.zig"),
        .target = target,
        .optimize = optimize,
    });

    // Integration tests
    const integration_tests = b.addTest(.{
        .root_source_file = b.path("tests/integration.zig"),
        .target = target,
        .optimize = optimize,
    });
    
    // Add the main module to integration tests
    integration_tests.root_module.addImport("mylib", b.addModule("mylib", .{
        .root_source_file = b.path("src/lib.zig"),
    }));

    const run_unit = b.addRunArtifact(unit_tests);
    const run_integration = b.addRunArtifact(integration_tests);

    const test_step = b.step("test", "Run all tests");
    test_step.dependOn(&run_unit.step);
    test_step.dependOn(&run_integration.step);
    
    // Separate steps for different test suites
    const unit_step = b.step("test-unit", "Run unit tests");
    unit_step.dependOn(&run_unit.step);
    
    const integration_step = b.step("test-integration", "Run integration tests");
    integration_step.dependOn(&run_integration.step);
}
```

## Best Practices

### 1. Test Behavior, Not Implementation

```zig
// ❌ BAD: Tests internal state
test "buffer has capacity 16" {
    const buf = Buffer.init();
    try testing.expectEqual(@as(usize, 16), buf.internal_capacity);
}

// ✅ GOOD: Tests observable behavior  
test "buffer can hold items" {
    var buf = Buffer.init(testing.allocator);
    defer buf.deinit();
    
    for (0..100) |i| try buf.append(@intCast(i));
    try testing.expectEqual(@as(usize, 100), buf.len());
}
```

### 2. Test Edge Cases

```zig
test "empty input" { ... }
test "single element" { ... }
test "maximum size" { ... }
test "special characters" { ... }
test "unicode" { ... }
```

### 3. Test Error Paths

```zig
test "success case" {
    const result = try operation();
    try testing.expect(result.valid);
}

test "handles invalid input" {
    try testing.expectError(error.InvalidInput, operation(null));
}

test "handles allocation failure" {
    var failing = testing.FailingAllocator.init(testing.allocator, .{ .fail_index = 0 });
    try testing.expectError(error.OutOfMemory, operation(failing.allocator()));
}
```

### 4. Use Descriptive Test Names

```zig
// ❌ BAD
test "test1" { ... }

// ✅ GOOD
test "Parser returns EmptyInput error for empty string" { ... }
test "Buffer doubles capacity when full" { ... }
```
