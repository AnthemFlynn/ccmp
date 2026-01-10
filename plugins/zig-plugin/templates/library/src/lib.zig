// Library Template
// A reusable Zig library with proper structure

const std = @import("std");
const Allocator = std.mem.Allocator;
const testing = std.testing;

/// Error types for this library
pub const Error = error{
    InvalidInput,
    OutOfMemory,
    OperationFailed,
};

/// Main library context
pub const Context = struct {
    allocator: Allocator,
    data: std.ArrayList(u8),
    
    const Self = @This();
    
    /// Initialize a new context
    pub fn init(allocator: Allocator) Self {
        return .{
            .allocator = allocator,
            .data = std.ArrayList(u8).init(allocator),
        };
    }
    
    /// Clean up resources
    pub fn deinit(self: *Self) void {
        self.data.deinit();
    }
    
    /// Process input data
    pub fn process(self: *Self, input: []const u8) Error![]const u8 {
        if (input.len == 0) {
            return error.InvalidInput;
        }
        
        self.data.clearRetainingCapacity();
        self.data.appendSlice(input) catch return error.OutOfMemory;
        
        // Transform: example operation
        for (self.data.items) |*byte| {
            byte.* = std.ascii.toUpper(byte.*);
        }
        
        return self.data.items;
    }
    
    /// Get current state
    pub fn getData(self: *const Self) []const u8 {
        return self.data.items;
    }
};

/// Standalone utility function
pub fn transform(allocator: Allocator, input: []const u8) Error![]u8 {
    if (input.len == 0) {
        return error.InvalidInput;
    }
    
    const result = allocator.alloc(u8, input.len) catch return error.OutOfMemory;
    for (input, 0..) |byte, i| {
        result[i] = std.ascii.toUpper(byte);
    }
    return result;
}

// ============================================================================
// Tests
// ============================================================================

test "Context: init and deinit" {
    var ctx = Context.init(testing.allocator);
    defer ctx.deinit();
}

test "Context: process valid input" {
    var ctx = Context.init(testing.allocator);
    defer ctx.deinit();
    
    const result = try ctx.process("hello");
    try testing.expectEqualStrings("HELLO", result);
}

test "Context: process empty input returns error" {
    var ctx = Context.init(testing.allocator);
    defer ctx.deinit();
    
    try testing.expectError(error.InvalidInput, ctx.process(""));
}

test "Context: multiple process calls" {
    var ctx = Context.init(testing.allocator);
    defer ctx.deinit();
    
    _ = try ctx.process("first");
    const result = try ctx.process("second");
    try testing.expectEqualStrings("SECOND", result);
}

test "transform: basic functionality" {
    const result = try transform(testing.allocator, "hello world");
    defer testing.allocator.free(result);
    
    try testing.expectEqualStrings("HELLO WORLD", result);
}

test "transform: empty input returns error" {
    try testing.expectError(error.InvalidInput, transform(testing.allocator, ""));
}
