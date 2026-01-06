# TDD Loop Workflow

Red-green-refactor cycle for Zig development using the test-first approach.

## Overview

This workflow guides test-driven development in Zig, leveraging:
- Zig's built-in test framework
- std.testing.allocator for memory leak detection
- Fast incremental compilation for tight feedback loops

## The Cycle

```
┌─────────────────────────────────────────────────────────┐
│  1. RED: Write a failing test                           │
│     ↓                                                   │
│  2. Run tests → verify failure (expected)               │
│     ↓                                                   │
│  3. GREEN: Write minimal code to pass                   │
│     ↓                                                   │
│  4. Run tests → verify success                          │
│     ↓                                                   │
│  5. REFACTOR: Improve code, tests still pass            │
│     ↓                                                   │
│  └──────── Back to step 1 ──────────┘                   │
└─────────────────────────────────────────────────────────┘
```

## Step-by-Step Process

### Step 1: Write a Failing Test

```zig
// src/calculator.zig
const std = @import("std");
const testing = std.testing;

// The test comes FIRST, before the implementation
test "add returns sum of two numbers" {
    const result = add(2, 3);
    try testing.expectEqual(@as(i32, 5), result);
}

// Minimal stub to make it compile (but fail the test)
pub fn add(a: i32, b: i32) i32 {
    _ = a;
    _ = b;
    return 0;  // Wrong on purpose
}
```

**Why this matters**: The failing test proves the test is actually testing something. If it passes immediately, the test might be broken.

### Step 2: Verify the Failure

Use the MCP tools:

```
→ zig_test(cwd: ".", filter: "add returns sum")

❌ Tests failed
  1 passed, 1 failed (45ms)

Failed tests:
  ❌ add returns sum of two numbers
     expected 5, found 0
```

The failure message should clearly indicate what's wrong.

### Step 3: Make It Pass (Minimally)

```zig
pub fn add(a: i32, b: i32) i32 {
    return a + b;  // Simplest implementation
}
```

**Principle**: Write the *minimum* code needed. Don't anticipate future requirements.

### Step 4: Verify Success

```
→ zig_test(cwd: ".", filter: "add")

✅ All tests passed!
  1 passed, 0 failed, 0 skipped (12ms)
```

### Step 5: Refactor

Now improve the code while keeping tests green:

```zig
/// Adds two integers, returning their sum.
/// 
/// Note: For checked arithmetic that detects overflow,
/// use std.math.add instead.
pub fn add(a: i32, b: i32) i32 {
    return a + b;
}
```

Run tests after each refactoring change to ensure nothing breaks.

## Testing with Allocators

For any code that allocates memory, use `std.testing.allocator`:

```zig
test "dynamic buffer grows correctly" {
    var buffer = try DynamicBuffer.init(std.testing.allocator);
    defer buffer.deinit();  // CRITICAL: cleanup on success
    
    try buffer.append("hello");
    try testing.expectEqual(@as(usize, 5), buffer.len());
}
```

The testing allocator will:
- ✅ Fail the test if any memory leaks
- ✅ Detect use-after-free
- ✅ Detect double-free

### Testing Error Paths

```zig
test "handles allocation failure" {
    // FailingAllocator fails after N allocations
    var failing_alloc = std.testing.FailingAllocator.init(
        std.testing.allocator,
        .{ .fail_index = 0 },  // Fail immediately
    );
    
    const result = DynamicBuffer.init(failing_alloc.allocator());
    try testing.expectError(error.OutOfMemory, result);
}
```

## Test Organization

### In-File Tests (Unit Tests)

Place tests next to the code they test:

```zig
// src/parser.zig

pub fn parse(input: []const u8) !Ast {
    // implementation
}

test "parse empty input returns empty ast" {
    const ast = try parse("");
    try testing.expect(ast.nodes.len == 0);
}

test "parse single token" {
    const ast = try parse("hello");
    try testing.expectEqual(@as(usize, 1), ast.nodes.len);
}
```

### Integration Tests (Separate Directory)

For tests that span multiple modules:

```
project/
├── src/
│   ├── parser.zig
│   ├── compiler.zig
│   └── runtime.zig
└── tests/
    └── integration.zig
```

```zig
// tests/integration.zig
const parser = @import("../src/parser.zig");
const compiler = @import("../src/compiler.zig");
const runtime = @import("../src/runtime.zig");

test "full pipeline: parse → compile → run" {
    const source = "print(1 + 2)";
    const ast = try parser.parse(source);
    const bytecode = try compiler.compile(ast);
    const output = try runtime.execute(bytecode);
    try std.testing.expectEqualStrings("3", output);
}
```

## MCP Tool Integration

### Tight Loop Commands

```
# Run specific test
→ zig_test(cwd: ".", filter: "my_test_name")

# Run all tests
→ zig_test(cwd: ".")

# Check formatting
→ zig_fmt(cwd: ".", path: "src/", check: true)
```

### Debugging Failed Tests

1. Get detailed error:
   ```
   → zig_test(cwd: ".", filter: "failing_test")
   ```

2. Check if it's a compilation error vs runtime failure

3. For runtime failures, add intermediate assertions:
   ```zig
   test "complex calculation" {
       const step1 = compute_first();
       std.debug.print("step1 = {}\n", .{step1});  // Debug output
       try testing.expectEqual(@as(i32, 10), step1);
       
       const step2 = compute_second(step1);
       // ...
   }
   ```

## Common TDD Patterns in Zig

### Testing Iterators

```zig
test "iterator yields expected values" {
    var iter = MyIterator.init("a,b,c");
    
    try testing.expectEqualStrings("a", iter.next().?);
    try testing.expectEqualStrings("b", iter.next().?);
    try testing.expectEqualStrings("c", iter.next().?);
    try testing.expect(iter.next() == null);
}
```

### Testing Errors

```zig
test "invalid input returns error" {
    const result = parse("invalid{{");
    try testing.expectError(error.InvalidSyntax, result);
}
```

### Testing Optionals

```zig
test "find returns item when present" {
    const items = [_]i32{ 1, 2, 3, 4, 5 };
    const found = find(&items, 3);
    try testing.expect(found != null);
    try testing.expectEqual(@as(i32, 3), found.?.*);
}

test "find returns null when absent" {
    const items = [_]i32{ 1, 2, 3, 4, 5 };
    try testing.expect(find(&items, 99) == null);
}
```

## Anti-Patterns to Avoid

### ❌ Testing Implementation Details

```zig
// BAD: Tests internal buffer size
test "buffer starts with capacity 16" {
    const buf = Buffer.init();
    try testing.expectEqual(@as(usize, 16), buf.capacity);
}
```

### ✅ Test Behavior Instead

```zig
// GOOD: Tests observable behavior
test "buffer can hold at least 100 items initially" {
    var buf = Buffer.init(std.testing.allocator);
    defer buf.deinit();
    
    for (0..100) |i| {
        try buf.append(@intCast(i));
    }
    try testing.expectEqual(@as(usize, 100), buf.len());
}
```

### ❌ Ignoring Error Paths

```zig
// BAD: Only tests happy path
test "parse works" {
    _ = try parse("valid");
}
```

### ✅ Test Error Cases Too

```zig
// GOOD: Tests both success and failure
test "parse valid input" {
    const result = try parse("valid");
    try testing.expect(result.nodes.len > 0);
}

test "parse invalid input returns error" {
    try testing.expectError(error.InvalidSyntax, parse("{{bad"));
}

test "parse handles empty input" {
    const result = try parse("");
    try testing.expectEqual(@as(usize, 0), result.nodes.len);
}
```
