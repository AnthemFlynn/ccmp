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

export function parseZigErrors(output: string): ZigError[] {
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
// ZVM/ZLS Tool Implementations
// ============================================================================

async function zvmInstall(args: {
  version: string;
  withZls?: boolean;
  force?: boolean;
}): Promise<object> {
  const cmdArgs = ["zvm", "i", args.version];
  if (args.withZls !== false) cmdArgs.push("--zls");
  if (args.force) cmdArgs.push("-f");

  const result = await runCommand(cmdArgs);

  return {
    success: result.exitCode === 0,
    version: args.version,
    zlsInstalled: args.withZls !== false,
    stdout: result.stdout,
    stderr: result.stderr,
    durationMs: result.durationMs,
  };
}

async function zvmUse(args: { version: string }): Promise<object> {
  const result = await runCommand(["zvm", "use", args.version]);

  return {
    success: result.exitCode === 0,
    activeVersion: args.version,
    stdout: result.stdout,
    stderr: result.stderr,
  };
}

export function parseZvmList(output: string): { installed: string[]; active: string | null } {
  const lines = output.split("\n").filter((l) => l.trim());
  const installed: string[] = [];
  let active: string | null = null;

  for (const line of lines) {
    // ZVM marks active version with arrow or asterisk
    const isActive = line.includes("*") || line.includes("←") || line.includes("<-");
    // Clean up the version string - remove markers and whitespace
    const version = line.replace(/[*←<>\s]/g, "").replace(/-$/, "").trim();
    if (version && !version.includes("---")) {
      installed.push(version);
      if (isActive) active = version;
    }
  }

  return { installed, active };
}

async function zvmList(): Promise<object> {
  const result = await runCommand(["zvm", "ls"]);

  if (result.exitCode !== 0) {
    return {
      success: false,
      installed: [],
      active: null,
      error: result.stderr || "ZVM not found",
    };
  }

  const parsed = parseZvmList(result.stdout);

  return {
    success: true,
    ...parsed,
  };
}

async function zlsStatus(): Promise<object> {
  // Check ZLS
  const zlsResult = await runCommand(["zls", "--version"]);
  const zigResult = await runCommand(["zig", "version"]);

  if (zlsResult.exitCode !== 0) {
    return {
      installed: false,
      path: null,
      version: null,
      compatible: false,
      zigVersion: zigResult.stdout.trim() || null,
      error: "ZLS not found in PATH",
    };
  }

  // Get ZLS path
  const whichResult = await runCommand(["which", "zls"]);
  const zlsPath = whichResult.stdout.trim();
  const zlsVersion = zlsResult.stdout.trim();
  const zigVersion = zigResult.stdout.trim();

  // Check compatibility - versions should match for nightly
  // For tagged releases, major.minor should match
  const compatible = zlsVersion.includes(zigVersion.split(".").slice(0, 2).join("."));

  return {
    installed: true,
    path: zlsPath,
    version: zlsVersion,
    compatible,
    zigVersion,
  };
}

async function zigFetch(args: { url: string; cwd: string }): Promise<object> {
  const result = await runCommand(["zig", "fetch", "--save", args.url], args.cwd);

  // Extract hash from output if successful
  const hashMatch = result.stdout.match(/([a-f0-9]{64})/i);

  return {
    success: result.exitCode === 0,
    hash: hashMatch ? hashMatch[1] : null,
    stdout: result.stdout,
    stderr: result.stderr,
  };
}

async function zigCheck(args: {
  cwd: string;
  file?: string;
}): Promise<object> {
  // Use 'zig build' with emit mode disabled for fast syntax/type checking
  const cmdArgs = ["zig", "build"];

  // If checking a single file, we need a different approach
  // For now, just do a quick build check
  if (args.file) {
    // Use zig ast-check for single file syntax validation
    const result = await runCommand(["zig", "ast-check", args.file], args.cwd);
    const errors = parseZigErrors(result.stderr);

    return {
      success: result.exitCode === 0,
      file: args.file,
      errors,
      durationMs: result.durationMs,
      stderr: result.stderr,
    };
  }

  // For project-wide check, use build with summary
  const result = await runCommand(cmdArgs, args.cwd);
  const errors = parseZigErrors(result.stderr);

  return {
    success: result.exitCode === 0,
    errors,
    durationMs: result.durationMs,
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
    {
      name: "zig_check",
      description: "Fast syntax and type checking without full build. Use for tight TDD feedback loops. For single files, uses ast-check; for projects, runs build.",
      inputSchema: {
        type: "object" as const,
        properties: {
          cwd: {
            type: "string",
            description: "Working directory containing build.zig or the file",
          },
          file: {
            type: "string",
            description: "Optional: single .zig file to check (uses ast-check)",
          },
        },
        required: ["cwd"],
      },
    },
    // ZVM Tools
    {
      name: "zvm_install",
      description: "Install a Zig version using ZVM (Zig Version Manager). Optionally installs matching ZLS.",
      inputSchema: {
        type: "object" as const,
        properties: {
          version: {
            type: "string",
            description: "Zig version to install (e.g., 'master', '0.13.0')",
          },
          withZls: {
            type: "boolean",
            description: "Install matching ZLS version (default: true for master/nightly)",
          },
          force: {
            type: "boolean",
            description: "Force reinstall even if already installed",
          },
        },
        required: ["version"],
      },
    },
    {
      name: "zvm_use",
      description: "Switch to a different installed Zig version.",
      inputSchema: {
        type: "object" as const,
        properties: {
          version: {
            type: "string",
            description: "Version to activate",
          },
        },
        required: ["version"],
      },
    },
    {
      name: "zvm_list",
      description: "List all installed Zig versions and show which is active.",
      inputSchema: {
        type: "object" as const,
        properties: {},
      },
    },
    {
      name: "zls_status",
      description: "Check ZLS (Zig Language Server) installation status and compatibility with current Zig version.",
      inputSchema: {
        type: "object" as const,
        properties: {},
      },
    },
    {
      name: "zig_fetch",
      description: "Add a dependency to build.zig.zon using zig fetch --save.",
      inputSchema: {
        type: "object" as const,
        properties: {
          url: {
            type: "string",
            description: "Package URL (e.g., GitHub tarball URL)",
          },
          cwd: {
            type: "string",
            description: "Project directory containing build.zig.zon",
          },
        },
        required: ["url", "cwd"],
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
    case "zig_check":
      result = await zigCheck(args as { cwd: string; file?: string });
      break;
    case "zvm_install":
      result = await zvmInstall(args as { version: string; withZls?: boolean; force?: boolean });
      break;
    case "zvm_use":
      result = await zvmUse(args as { version: string });
      break;
    case "zvm_list":
      result = await zvmList();
      break;
    case "zls_status":
      result = await zlsStatus();
      break;
    case "zig_fetch":
      result = await zigFetch(args as { url: string; cwd: string });
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
