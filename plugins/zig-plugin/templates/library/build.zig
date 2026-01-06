const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // Library module (can be imported by other Zig projects)
    const lib_mod = b.addModule("mylib", .{
        .root_source_file = b.path("src/lib.zig"),
        .target = target,
        .optimize = optimize,
    });

    // Static library artifact
    const lib = b.addStaticLibrary(.{
        .name = "mylib",
        .root_source_file = b.path("src/lib.zig"),
        .target = target,
        .optimize = optimize,
    });
    b.installArtifact(lib);

    // Shared library (optional)
    const shared_lib = b.addSharedLibrary(.{
        .name = "mylib",
        .root_source_file = b.path("src/lib.zig"),
        .target = target,
        .optimize = optimize,
    });
    
    const shared_step = b.step("shared", "Build shared library");
    shared_step.dependOn(&b.addInstallArtifact(shared_lib, .{}).step);

    // Unit tests
    const lib_tests = b.addTest(.{
        .root_source_file = b.path("src/lib.zig"),
        .target = target,
        .optimize = optimize,
    });

    const run_lib_tests = b.addRunArtifact(lib_tests);
    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&run_lib_tests.step);

    // Example executable using the library
    const example = b.addExecutable(.{
        .name = "example",
        .root_source_file = b.path("examples/main.zig"),
        .target = target,
        .optimize = optimize,
    });
    example.root_module.addImport("mylib", lib_mod);

    const example_step = b.step("example", "Build and run example");
    const run_example = b.addRunArtifact(example);
    example_step.dependOn(&run_example.step);

    // Documentation: use `zig build-lib -femit-docs` directly
    // or integrate with your preferred doc generator
}
