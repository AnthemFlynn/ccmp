#!/usr/bin/env bun
/**
 * Zig MCP Server for Claude Code
 * Provides compiler integration tools for Zig development
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { spawn } from "child_process";

// ============================================================================
// Types
// ============================================================================

interface ZigError {
  file: string;
  line: number;
  column: number;
  kind: "error" | "warning" | "note";
  message: string;
}

interface CommandResult {
  stdout: string;
  stderr: string;
  exitCode: number;
  durationMs: number;
}

// ============================================================================
// Zig Command Execution
// ============================================================================

async function runCommand(
  args: string[],
  cwd?: string
): Promise<CommandResult> {
  const start = Date.now();

  return new Promise((resolve) => {
    const proc = spawn(args[0], args.slice(1), {
      cwd: cwd || process.cwd(),
      shell: false,
    });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (data) => (stdout += data.toString()));
    proc.stderr.on("data", (data) => (stderr += data.toString()));

    proc.on("close", (code) => {
      resolve({
        stdout,
        stderr,
        exitCode: code ?? 1,
        durationMs: Date.now() - start,
      });
    });

    proc.on("error", (err) => {
      resolve({
        stdout: "",
        stderr: err.message,
        exitCode: 1,
        durationMs: Date.now() - start,
      });
    });
  });
}

function parseZigErrors(output: string): ZigError[] {
  const errors: ZigError[] = [];
  const lines = output.split("\n");

  for (const line of lines) {
    // Match: file:line:col: kind: message
    // Handle Windows paths (C:\foo.zig:10:5:)
    const match = line.match(
      /^(.+?):(\d+):(\d+):\s*(error|warning|note):\s*(.+)$/
    );
    if (match) {
      errors.push({
        file: match[1],
        line: parseInt(match[2], 10),
        column: parseInt(match[3], 10),
        kind: match[4] as "error" | "warning" | "note",
        message: match[5],
      });
    }
  }

  return errors;
}

// ============================================================================
// Tool Implementations
// ============================================================================

async function zigBuild(args: {
  cwd: string;
  target?: string;
  step?: string;
}): Promise<object> {
  const cmdArgs = ["zig", "build"];
  if (args.step) cmdArgs.push(args.step);
  if (args.target) cmdArgs.push(`-Dtarget=${args.target}`);

  const result = await runCommand(cmdArgs, args.cwd);
  const errors = parseZigErrors(result.stderr);

  return {
    success: result.exitCode === 0,
    exitCode: result.exitCode,
    durationMs: result.durationMs,
    stdout: result.stdout,
    stderr: result.stderr,
    errors,
  };
}

async function zigTest(args: {
  cwd: string;
  filter?: string;
}): Promise<object> {
  const cmdArgs = ["zig", "build", "test"];
  if (args.filter) cmdArgs.push(`--test-filter=${args.filter}`);

  const result = await runCommand(cmdArgs, args.cwd);

  // Parse test results from output
  // Zig test output varies by version, try multiple patterns
  const output = result.stdout + result.stderr;
  
  // Pattern 1: "X passed, Y failed"
  const passedMatch = output.match(/(\d+)\s+passed/);
  const failedMatch = output.match(/(\d+)\s+failed/);
  const skippedMatch = output.match(/(\d+)\s+skipped/);
  
  // Pattern 2: "All N tests passed" (older versions)
  const allPassedMatch = output.match(/All\s+(\d+)\s+tests?\s+passed/i);

  let passed = passedMatch ? parseInt(passedMatch[1], 10) : 0;
  const failed = failedMatch ? parseInt(failedMatch[1], 10) : 0;
  const skipped = skippedMatch ? parseInt(skippedMatch[1], 10) : 0;
  
  if (allPassedMatch && passed === 0) {
    passed = parseInt(allPassedMatch[1], 10);
  }

  // Check for "no tests" case
  const noTests = output.includes("no tests to run") || 
                  output.includes("0 tests") ||
                  (passed === 0 && failed === 0 && result.exitCode === 0);

  // Parse any compile errors
  const errors = parseZigErrors(result.stderr);

  return {
    success: result.exitCode === 0 && failed === 0,
    passed,
    failed,
    skipped,
    noTests: noTests && passed === 0,
    durationMs: result.durationMs,
    errors,
    stdout: result.stdout,
    stderr: result.stderr,
  };
}

async function zigVersion(): Promise<object> {
  const result = await runCommand(["zig", "version"]);

  if (result.exitCode !== 0) {
    return {
      installed: false,
      version: null,
      error: "Zig not found in PATH. Install from https://ziglang.org/download/",
    };
  }

  const version = result.stdout.trim();
  
  // Parse version components
  const versionMatch = version.match(/^(\d+)\.(\d+)\.(\d+)/);
  
  return {
    installed: true,
    version,
    major: versionMatch ? parseInt(versionMatch[1], 10) : null,
    minor: versionMatch ? parseInt(versionMatch[2], 10) : null,
    patch: versionMatch ? parseInt(versionMatch[3], 10) : null,
  };
}

async function zigInit(args: { cwd: string; template?: string }): Promise<object> {
  const cmdArgs = ["zig", "init"];
  
  const result = await runCommand(cmdArgs, args.cwd);

  return {
    success: result.exitCode === 0,
    stdout: result.stdout,
    stderr: result.stderr,
    files: result.exitCode === 0 
      ? ["build.zig", "build.zig.zon", "src/main.zig", "src/root.zig"]
      : [],
  };
}

async function zigFmt(args: { path: string; check?: boolean; cwd?: string }): Promise<object> {
  const cmdArgs = ["zig", "fmt"];
  if (args.check) cmdArgs.push("--check");
  cmdArgs.push(args.path);

  const result = await runCommand(cmdArgs, args.cwd);

  // Parse which files would be/were formatted
  const wouldFormat = result.stdout
    .split("\n")
    .filter((line) => line.trim().length > 0);

  return {
    success: result.exitCode === 0,
    formatted: !args.check && result.exitCode === 0,
    needsFormatting: args.check && result.exitCode !== 0,
    files: wouldFormat,
    stdout: result.stdout,
    stderr: result.stderr,
  };
}

async function zigTranslateC(args: {
  header: string;
  cwd?: string;
  includes?: string[];
  defines?: string[];
}): Promise<object> {
  const cmdArgs = ["zig", "translate-c"];

  if (args.includes) {
    for (const inc of args.includes) {
      cmdArgs.push("-I", inc);
    }
  }

  if (args.defines) {
    for (const def of args.defines) {
      cmdArgs.push(`-D${def}`);
    }
  }

  cmdArgs.push(args.header);

  const result = await runCommand(cmdArgs, args.cwd);

  return {
    success: result.exitCode === 0,
    zigCode: result.stdout,
    stderr: result.stderr,
  };
}

// ============================================================================
// MCP Server Setup
// ============================================================================

const server = new Server(
  {
    name: "zig-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "zig_build",
      description:
        "Build a Zig project. Returns structured error information including file, line, column for each compiler error.",
      inputSchema: {
        type: "object" as const,
        properties: {
          cwd: {
            type: "string",
            description: "Working directory containing build.zig",
          },
          target: {
            type: "string",
            description: "Cross-compilation target (e.g., x86_64-linux-gnu)",
          },
          step: {
            type: "string",
            description: "Build step to run (default: install)",
          },
        },
        required: ["cwd"],
      },
    },
    {
      name: "zig_test",
      description:
        "Run Zig tests. Returns pass/fail/skip counts and test output.",
      inputSchema: {
        type: "object" as const,
        properties: {
          cwd: {
            type: "string",
            description: "Working directory containing build.zig",
          },
          filter: {
            type: "string",
            description: "Filter tests by name",
          },
        },
        required: ["cwd"],
      },
    },
    {
      name: "zig_version",
      description: "Get the installed Zig version. Returns version components and installation status.",
      inputSchema: {
        type: "object" as const,
        properties: {},
      },
    },
    {
      name: "zig_init",
      description: "Initialize a new Zig project with build.zig and standard structure.",
      inputSchema: {
        type: "object" as const,
        properties: {
          cwd: {
            type: "string",
            description: "Directory to initialize the project in",
          },
        },
        required: ["cwd"],
      },
    },
    {
      name: "zig_fmt",
      description: "Format Zig source code. Returns list of files that were/would be formatted.",
      inputSchema: {
        type: "object" as const,
        properties: {
          path: {
            type: "string",
            description: "Path to file or directory to format",
          },
          cwd: {
            type: "string",
            description: "Working directory (for relative paths)",
          },
          check: {
            type: "boolean",
            description: "Check if formatting is needed without modifying",
          },
        },
        required: ["path"],
      },
    },
    {
      name: "zig_translate_c",
      description: "Translate a C header file to Zig code.",
      inputSchema: {
        type: "object" as const,
        properties: {
          header: {
            type: "string",
            description: "Path to C header file",
          },
          cwd: {
            type: "string",
            description: "Working directory",
          },
          includes: {
            type: "array",
            items: { type: "string" },
            description: "Include directories",
          },
          defines: {
            type: "array",
            items: { type: "string" },
            description: "Preprocessor definitions",
          },
        },
        required: ["header"],
      },
    },
  ],
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  let result: object;

  switch (name) {
    case "zig_build":
      result = await zigBuild(args as { cwd: string; target?: string; step?: string });
      break;
    case "zig_test":
      result = await zigTest(args as { cwd: string; filter?: string });
      break;
    case "zig_version":
      result = await zigVersion();
      break;
    case "zig_init":
      result = await zigInit(args as { cwd: string; template?: string });
      break;
    case "zig_fmt":
      result = await zigFmt(args as { path: string; check?: boolean; cwd?: string });
      break;
    case "zig_translate_c":
      result = await zigTranslateC(
        args as { header: string; cwd?: string; includes?: string[]; defines?: string[] }
      );
      break;
    default:
      throw new Error(`Unknown tool: ${name}`);
  }

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(result, null, 2),
      },
    ],
  };
});

// ============================================================================
// Main
// ============================================================================

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("zig-mcp server running on stdio");
}

main().catch(console.error);
