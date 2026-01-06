// CLI Application Template
// A well-structured Zig command-line application

const std = @import("std");
const builtin = @import("builtin");

// Configure logging level based on build mode
pub const std_options: std.Options = .{
    .log_level = if (builtin.mode == .Debug) .debug else .info,
};

pub fn main() !void {
    // Use GPA in debug for leak detection, page_allocator in release for speed
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer {
        const check = gpa.deinit();
        if (check == .leak) {
            std.log.err("Memory leak detected!", .{});
        }
    }
    const allocator = if (builtin.mode == .Debug)
        gpa.allocator()
    else
        std.heap.page_allocator;

    // Parse command-line arguments
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    if (args.len < 2) {
        try printUsage(args[0]);
        std.process.exit(1);
    }

    // Process command
    const command = args[1];
    const command_args = args[2..];

    if (std.mem.eql(u8, command, "help") or std.mem.eql(u8, command, "--help")) {
        try printUsage(args[0]);
        return;
    }

    if (std.mem.eql(u8, command, "version") or std.mem.eql(u8, command, "--version")) {
        try printVersion();
        return;
    }

    if (std.mem.eql(u8, command, "run")) {
        try runCommand(allocator, command_args);
        return;
    }

    std.log.err("Unknown command: {s}", .{command});
    std.process.exit(1);
}

fn printUsage(program_name: []const u8) !void {
    const stdout = std.io.getStdOut().writer();
    try stdout.print(
        \\Usage: {s} <command> [options]
        \\
        \\Commands:
        \\  run      Run the main operation
        \\  help     Show this help message
        \\  version  Show version information
        \\
        \\Options:
        \\  --help     Show help for a command
        \\  --verbose  Enable verbose output
        \\
    , .{program_name});
}

fn printVersion() !void {
    const stdout = std.io.getStdOut().writer();
    try stdout.writeAll("myapp version 0.1.0\n");
}

fn runCommand(allocator: std.mem.Allocator, args: []const []const u8) !void {
    _ = allocator;
    
    const stdout = std.io.getStdOut().writer();
    
    if (args.len == 0) {
        try stdout.writeAll("Running with no arguments\n");
        return;
    }
    
    try stdout.print("Running with arguments: ", .{});
    for (args, 0..) |arg, i| {
        if (i > 0) try stdout.writeAll(", ");
        try stdout.print("{s}", .{arg});
    }
    try stdout.writeAll("\n");
}

// Tests
test "basic functionality" {
    // Add unit tests here
}
