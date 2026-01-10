# Zig Development Plugin for Claude Code

A comprehensive plugin that enables effective Zig development in Claude Code through deep language understanding, compiler integration, and development workflows.

## Components

### 1. Skills (`skills/zig/`)

Knowledge layer providing Zig-specific patterns and best practices:

- **SKILL.md** - Main entry point with quick reference and decision trees
- **references/allocators.md** - Deep dive on allocator patterns (GPA, Arena, FixedBuffer)
- **references/comptime.md** - Compile-time metaprogramming
- **references/build-system.md** - build.zig mastery, cross-compilation
- **references/error-handling.md** - Error unions, errdefer patterns
- **references/testing.md** - Built-in test framework, testing allocator
- **references/c-interop.md** - C FFI, translate-c, building C code

### 2. MCP Server (`mcp-servers/zig-mcp/`)

TypeScript MCP server (runs with Bun) providing compiler integration:

| Tool | Description |
|------|-------------|
| `zig_build` | Build with structured error output |
| `zig_test` | Run tests with pass/fail/skip counts |
| `zig_version` | Get installed Zig version |
| `zig_fmt` | Format Zig code |
| `zig_translate_c` | Convert C headers to Zig |

### 3. Workflows (`workflows/`)

Multi-step development processes:

- **tdd-loop.md** - Test-driven development cycle with memory leak detection
- **c-wrapper.md** - Systematic C library wrapping guide

### 4. Templates (`templates/`)

Project scaffolding:

- **cli-app/** - Command-line application with proper error handling
- **library/** - Reusable library with tests and docs

## Installation

### Prerequisites

- [Bun](https://bun.sh/) runtime
- Zig installed and in PATH (any recent version)

### Install the Skill

Copy the `skills/zig/` directory to your Claude Code skills location:

```bash
cp -r skills/zig ~/.claude/skills/
```

### Install the MCP Server

```bash
cd mcp-servers/zig-mcp
bun install
```

### Configure Claude Code

Add to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "zig": {
      "command": "bun",
      "args": ["run", "/path/to/zig-plugin/mcp-servers/zig-mcp/src/index.ts"]
    }
  }
}
```

## Why This Plugin?

### What LLMs Get Wrong About Zig

1. **Allocators** - Creating allocators in wrong scope, forgetting `errdefer`
2. **Comptime** - Confusing runtime/compile-time contexts
3. **Error Handling** - Using `catch unreachable` for recoverable errors
4. **Build System** - Wrong APIs, missing linkLibC, etc.

### How This Plugin Helps

- **Skills** encode correct patterns with explicit anti-pattern examples
- **MCP Server** provides immediate compiler feedback with structured errors
- **Workflows** guide multi-step processes correctly

## Version Compatibility

The MCP server calls `zig` commands and parses their output - it works with any Zig version. The skills and templates are version-agnostic patterns that apply across Zig releases.

## Development

### Testing the MCP Server

```bash
cd mcp-servers/zig-mcp
bun run src/index.ts
# Server runs on stdio, use Ctrl+C to exit
```

## License

MIT
