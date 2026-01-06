// Example usage of the library
const std = @import("std");
const mylib = @import("mylib");

pub fn main() !void {
    // Use GPA for memory management
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const stdout = std.io.getStdOut().writer();

    // Example 1: Using the Context struct
    var ctx = mylib.Context.init(allocator);
    defer ctx.deinit();

    const result = ctx.process("hello, zig!") catch |err| {
        try stdout.print("Error: {}\n", .{err});
        return;
    };
    try stdout.print("Processed: {s}\n", .{result});

    // Example 2: Using standalone transform function
    const transformed = mylib.transform(allocator, "standalone function") catch |err| {
        try stdout.print("Error: {}\n", .{err});
        return;
    };
    defer allocator.free(transformed);
    try stdout.print("Transformed: {s}\n", .{transformed});
}
