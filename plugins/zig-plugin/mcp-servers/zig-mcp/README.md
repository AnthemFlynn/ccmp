# Zig MCP Server

MCP (Model Context Protocol) server providing Zig compiler integration for Claude Code.

## Requirements

- [Bun](https://bun.sh/) runtime
- Zig compiler installed and in PATH

## Installation

```bash
cd mcp-servers/zig-mcp
bun install
```

## Usage

### With Claude Code

Add to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "zig": {
      "command": "bun",
      "args": ["run", "/path/to/zig-mcp/src/index.ts"]
    }
  }
}
```

### Standalone

```bash
bun run src/index.ts
```

## Tools

### zig_build

Build a Zig project with structured error reporting.

```json
{
  "cwd": "/path/to/project",
  "target": "x86_64-linux-gnu",  // optional
  "step": "install"               // optional
}
```

Returns:
- `success`: boolean
- `errors`: Array of `{file, line, column, kind, message}`
- `exitCode`: number
- `durationMs`: Build time
- `stdout`, `stderr`: Raw output

### zig_test

Run tests with detailed results.

```json
{
  "cwd": "/path/to/project",
  "filter": "test_name"  // optional
}
```

Returns:
- `success`: boolean
- `passed`, `failed`, `skipped`: Test counts
- `noTests`: boolean (true if no tests found)
- `errors`: Array of compile errors if any
- `durationMs`: Test time
- `stdout`, `stderr`: Test output

### zig_version

Check Zig installation.

```json
{}
```

Returns:
- `installed`: boolean
- `version`: string (e.g., "0.14.1")
- `major`, `minor`, `patch`: number (parsed version components)
- `error`: string (if not installed)

### zig_init

Initialize a new Zig project.

```json
{
  "cwd": "/path/to/new/project"
}
```

Returns:
- `success`: boolean
- `files`: Array of created files
- `stdout`, `stderr`: Command output

### zig_fmt

Format Zig source files.

```json
{
  "path": "/path/to/file.zig",
  "cwd": "/working/dir",     // optional
  "check": true              // optional, don't modify
}
```

Returns:
- `success`: boolean
- `formatted`: boolean (if files were formatted)
- `needsFormatting`: boolean (if check mode and files need formatting)
- `files`: Array of affected files
- `stdout`, `stderr`: Command output

### zig_translate_c

Translate C headers to Zig.

```json
{
  "header": "/path/to/header.h",
  "cwd": "/working/dir",           // optional
  "includes": ["/usr/include"],    // optional
  "defines": ["DEBUG"]             // optional
}
```

Returns:
- `success`: boolean
- `zigCode`: Translated Zig source
- `stderr`: Any warnings/errors
