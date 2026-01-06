# Build System Deep Dive

Zig's build system is written in Zig itself. `build.zig` is executable code, not a DSL, giving you full language power for build configuration.

## Build System Fundamentals

### Minimal build.zig

```zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    // Standard target and optimization options
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // Executable
    const exe = b.addExecutable(.{
        .name = "myapp",
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });
    b.installArtifact(exe);

    // Run command: `zig build run`
    const run_cmd = b.addRunArtifact(exe);
    run_cmd.step.dependOn(b.getInstallStep());
    if (b.args) |args| run_cmd.addArgs(args);

    const run_step = b.step("run", "Run the application");
    run_step.dependOn(&run_cmd.step);

    // Test command: `zig build test`
    const tests = b.addTest(.{
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&run_tests.step);
}
```

### Library Build

```zig
pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // Static library
    const lib = b.addStaticLibrary(.{
        .name = "mylib",
        .root_source_file = b.path("src/lib.zig"),
        .target = target,
        .optimize = optimize,
    });
    b.installArtifact(lib);

    // Shared library (optional)
    const shared = b.addSharedLibrary(.{
        .name = "mylib",
        .root_source_file = b.path("src/lib.zig"),
        .target = target,
        .optimize = optimize,
    });
    b.installArtifact(shared);

    // Module for other Zig projects to import
    _ = b.addModule("mylib", .{
        .root_source_file = b.path("src/lib.zig"),
    });
}
```

## Package Management (build.zig.zon)

### Package Manifest

```zig
// build.zig.zon
.{
    .name = "myproject",
    .version = "0.1.0",
    .minimum_zig_version = "0.13.0",
    
    .dependencies = .{
        // Git dependency
        .@"zig-network" = .{
            .url = "https://github.com/marler/zig-network/archive/refs/tags/v0.7.0.tar.gz",
            .hash = "122013f...",
        },
        
        // Local dependency (for development)
        .@"my-local-lib" = .{
            .path = "../my-local-lib",
        },
    },
    
    .paths = .{
        "build.zig",
        "build.zig.zon",
        "src",
        "LICENSE",
        "README.md",
    },
}
```

### Using Dependencies in build.zig

```zig
pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // Get dependency
    const network_dep = b.dependency("zig-network", .{
        .target = target,
        .optimize = optimize,
    });

    const exe = b.addExecutable(.{
        .name = "myapp",
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });

    // Add module from dependency
    exe.root_module.addImport("network", network_dep.module("network"));
    
    b.installArtifact(exe);
}
```

### Fetching Dependencies

```bash
# Fetch and compute hash for new dependency
zig fetch https://github.com/user/repo/archive/v1.0.0.tar.gz

# Update all dependencies
zig build --fetch
```

## C Integration

### Linking C Libraries

```zig
pub fn build(b: *std.Build) void {
    const exe = b.addExecutable(.{
        .name = "myapp",
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });

    // System library
    exe.linkSystemLibrary("sqlite3");
    exe.linkSystemLibrary("ssl");
    exe.linkSystemLibrary("crypto");
    
    // libc (usually needed for C libs)
    exe.linkLibC();

    // Library search paths
    exe.addLibraryPath(.{ .cwd_relative = "/opt/mylibs/lib" });
    exe.addIncludePath(.{ .cwd_relative = "/opt/mylibs/include" });

    b.installArtifact(exe);
}
```

### Building C Sources

```zig
pub fn build(b: *std.Build) void {
    const exe = b.addExecutable(.{
        .name = "myapp",
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });

    // Add C source files
    exe.addCSourceFiles(.{
        .files = &.{
            "vendor/sqlite3.c",
            "vendor/lz4.c",
        },
        .flags = &.{
            "-DSQLITE_ENABLE_FTS5",
            "-DSQLITE_THREADSAFE=1",
            "-O2",
        },
    });

    // Include directories for C headers
    exe.addIncludePath(b.path("vendor"));
    
    exe.linkLibC();
    b.installArtifact(exe);
}
```

### translate-c Integration

```zig
pub fn build(b: *std.Build) void {
    const exe = b.addExecutable(.{ ... });

    // Import C header as Zig module
    exe.root_module.addImport("clib", b.addTranslateCStep(.{
        .root_source_file = b.path("vendor/clib.h"),
    }).getModule());

    b.installArtifact(exe);
}
```

## Cross-Compilation

### Target Selection

```zig
pub fn build(b: *std.Build) void {
    // Let user specify target via -Dtarget=...
    const target = b.standardTargetOptions(.{});

    // Or hardcode specific targets
    const targets = [_]std.Target.Query{
        .{ .cpu_arch = .x86_64, .os_tag = .linux, .abi = .gnu },
        .{ .cpu_arch = .x86_64, .os_tag = .linux, .abi = .musl },
        .{ .cpu_arch = .aarch64, .os_tag = .linux, .abi = .gnu },
        .{ .cpu_arch = .x86_64, .os_tag = .windows, .abi = .gnu },
        .{ .cpu_arch = .x86_64, .os_tag = .macos },
        .{ .cpu_arch = .aarch64, .os_tag = .macos },
        .{ .cpu_arch = .wasm32, .os_tag = .wasi },
    };

    for (targets) |t| {
        const exe = b.addExecutable(.{
            .name = "myapp",
            .root_source_file = b.path("src/main.zig"),
            .target = b.resolveTargetQuery(t),
            .optimize = optimize,
        });
        
        const target_output = b.addInstallArtifact(exe, .{
            .dest_dir = .{
                .override = .{ .custom = @tagName(t.cpu_arch) ++ "-" ++ @tagName(t.os_tag) },
            },
        });
        
        b.getInstallStep().dependOn(&target_output.step);
    }
}
```

### Cross-Compilation with C

```zig
pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});

    const exe = b.addExecutable(.{
        .name = "myapp",
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });

    // Use Zig's bundled libc for cross-compilation
    // This eliminates the need for target-specific sysroots
    exe.linkLibC();

    // For musl targets, Zig provides a complete libc
    // For glibc targets, you may need system libraries

    b.installArtifact(exe);
}
```

## Build Steps and Custom Commands

### Custom Build Steps

```zig
pub fn build(b: *std.Build) void {
    // Code generation step
    const gen = b.addExecutable(.{
        .name = "codegen",
        .root_source_file = b.path("tools/codegen.zig"),
    });

    const gen_cmd = b.addRunArtifact(gen);
    gen_cmd.addArg("--output");
    const generated = gen_cmd.addOutputFileArg("generated.zig");
    gen_cmd.addFileArg(b.path("schema.json"));

    // Main executable uses generated code
    const exe = b.addExecutable(.{
        .name = "myapp",
        .root_source_file = b.path("src/main.zig"),
    });
    exe.root_module.addAnonymousImport("generated", .{
        .root_source_file = generated,
    });
}
```

### System Commands

```zig
pub fn build(b: *std.Build) void {
    // Run external command
    const protoc = b.addSystemCommand(&.{
        "protoc",
        "--zig_out=src/gen",
        "proto/messages.proto",
    });

    const exe = b.addExecutable(.{ ... });
    exe.step.dependOn(&protoc.step);
}
```

### Embed Files

```zig
pub fn build(b: *std.Build) void {
    const exe = b.addExecutable(.{
        .name = "myapp",
        .root_source_file = b.path("src/main.zig"),
    });

    // Embed file at compile time
    exe.root_module.addAnonymousImport("config", .{
        .root_source_file = b.path("config.json"),
    });

    // In Zig code:
    // const config = @import("config");
    // const data = @embedFile("config");
}
```

## Build Modes and Options

### Custom Options

```zig
pub fn build(b: *std.Build) void {
    // Boolean option: -Denable-feature=true
    const enable_feature = b.option(bool, "enable-feature", "Enable experimental feature") orelse false;

    // String option: -Dapi-key=xxx
    const api_key = b.option([]const u8, "api-key", "API key for external service");

    // Enum option: -Dlog-level=debug
    const LogLevel = enum { debug, info, warn, err };
    const log_level = b.option(LogLevel, "log-level", "Logging level") orelse .info;

    const exe = b.addExecutable(.{ ... });

    // Pass options to code
    const options = b.addOptions();
    options.addOption(bool, "enable_feature", enable_feature);
    options.addOption(?[]const u8, "api_key", api_key);
    options.addOption(LogLevel, "log_level", log_level);
    
    exe.root_module.addOptions("config", options);
    
    // In code: const config = @import("config");
    // if (config.enable_feature) { ... }
}
```

### Build Configuration

```zig
pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    
    // optimize is one of:
    // .Debug - Fast compile, runtime safety, no optimization
    // .ReleaseSafe - Optimized, keeps runtime safety
    // .ReleaseFast - Maximum optimization, no safety
    // .ReleaseSmall - Optimize for size
    
    const exe = b.addExecutable(.{
        .name = "myapp",
        .root_source_file = b.path("src/main.zig"),
        .optimize = optimize,
        .strip = optimize != .Debug,  // Strip symbols in release
        .single_threaded = false,      // Enable threading
    });
}
```

## Testing Configuration

### Test Filters and Options

```zig
pub fn build(b: *std.Build) void {
    const tests = b.addTest(.{
        .root_source_file = b.path("src/main.zig"),
    });

    // Filter tests by name
    if (b.option([]const u8, "test-filter", "Filter tests by name")) |filter| {
        tests.setFilter(filter);
    }

    const run_tests = b.addRunArtifact(tests);
    
    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_tests.step);
}
```

### Integration Tests

```zig
pub fn build(b: *std.Build) void {
    // Unit tests (in src/)
    const unit_tests = b.addTest(.{
        .root_source_file = b.path("src/lib.zig"),
    });

    // Integration tests (separate directory)
    const integration_tests = b.addTest(.{
        .root_source_file = b.path("tests/integration.zig"),
    });
    integration_tests.root_module.addImport("mylib", b.addModule("mylib", .{
        .root_source_file = b.path("src/lib.zig"),
    }));

    const test_step = b.step("test", "Run all tests");
    test_step.dependOn(&b.addRunArtifact(unit_tests).step);
    test_step.dependOn(&b.addRunArtifact(integration_tests).step);
}
```

## Common Patterns

### Library + Executable

```zig
pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // Library module (shared between lib and exe)
    const lib_mod = b.addModule("mylib", .{
        .root_source_file = b.path("src/lib.zig"),
        .target = target,
        .optimize = optimize,
    });

    // Static library
    const lib = b.addStaticLibrary(.{
        .name = "mylib",
        .root_module = lib_mod,
    });
    b.installArtifact(lib);

    // Executable using the library
    const exe = b.addExecutable(.{
        .name = "myapp",
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });
    exe.root_module.addImport("mylib", lib_mod);
    b.installArtifact(exe);
}
```

### Monorepo with Multiple Packages

```zig
pub fn build(b: *std.Build) void {
    const packages = [_][]const u8{ "core", "cli", "web", "utils" };
    
    for (packages) |pkg| {
        const exe = b.addExecutable(.{
            .name = pkg,
            .root_source_file = b.path(b.fmt("packages/{s}/src/main.zig", .{pkg})),
        });
        b.installArtifact(exe);
        
        const run_cmd = b.addRunArtifact(exe);
        const run_step = b.step(b.fmt("run-{s}", .{pkg}), b.fmt("Run {s}", .{pkg}));
        run_step.dependOn(&run_cmd.step);
    }
}
```
