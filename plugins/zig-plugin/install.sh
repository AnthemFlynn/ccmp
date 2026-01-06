#!/bin/bash
# Zig Plugin Installer
# Installs MCP server dependencies and verifies required tools

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MCP_DIR="$SCRIPT_DIR/mcp-servers/zig-mcp"

echo "=========================================="
echo "  Zig Plugin Installer"
echo "=========================================="
echo ""

# Check Bun runtime (required for MCP server)
echo "Checking dependencies..."
if ! command -v bun &> /dev/null; then
    echo "❌ Bun not found."
    echo ""
    echo "   Install Bun from https://bun.sh/"
    echo "   curl -fsSL https://bun.sh/install | bash"
    echo ""
    exit 1
fi

BUN_VERSION=$(bun --version 2>/dev/null || echo "unknown")
echo "✓ Bun $BUN_VERSION"

# Check ZVM (Zig Version Manager)
if command -v zvm &> /dev/null; then
    ZVM_VERSION=$(zvm --version 2>/dev/null || echo "unknown")
    echo "✓ ZVM $ZVM_VERSION"
else
    echo "⚠️  ZVM not found (recommended for managing Zig versions)"
    echo "   Install from: https://github.com/tristanisham/zvm"
    echo "   Or run: curl -fsSL https://raw.githubusercontent.com/tristanisham/zvm/master/install.sh | bash"
    echo ""
fi

# Check Zig compiler
if command -v zig &> /dev/null; then
    ZIG_VERSION=$(zig version 2>/dev/null || echo "unknown")
    echo "✓ Zig $ZIG_VERSION"
else
    echo "⚠️  Zig not found (MCP tools will not work without it)"
    if command -v zvm &> /dev/null; then
        echo "   Install via ZVM: zvm i master --zls"
    else
        echo "   Install from https://ziglang.org/download/"
    fi
    echo ""
fi

# Check ZLS (Zig Language Server)
if command -v zls &> /dev/null; then
    ZLS_VERSION=$(zls --version 2>/dev/null || echo "unknown")
    echo "✓ ZLS $ZLS_VERSION"
else
    echo "⚠️  ZLS not found (required for editor integration)"
    if command -v zvm &> /dev/null; then
        echo "   Install via ZVM: zvm i master --zls"
    else
        echo "   Install from https://github.com/zigtools/zls"
    fi
    echo ""
fi

# Install MCP server dependencies
echo ""
echo "Installing MCP server dependencies..."
cd "$MCP_DIR"

if bun install; then
    echo "✓ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Verify server can start
echo ""
echo "Verifying MCP server..."
if timeout 2 bun run src/index.ts 2>&1 | grep -q "running"; then
    echo "✓ MCP server verified"
else
    echo "⚠️  Could not verify server (may still work)"
fi

# Success message
echo ""
echo "=========================================="
echo "✅ Zig plugin installed successfully!"
echo "=========================================="
echo ""
echo "To use the MCP server, add to your Claude Code config:"
echo ""
echo "  ~/.claude.json (or project .claude/settings.json):"
echo ""
cat << EOF
  {
    "mcpServers": {
      "zig": {
        "command": "bun",
        "args": ["run", "$MCP_DIR/src/index.ts"]
      }
    }
  }
EOF
echo ""
echo "Available MCP tools:"
echo ""
echo "  Build:"
echo "    • zig_build   - Build project with structured error output"
echo "    • zig_test    - Run tests with pass/fail counts"
echo "    • zig_check   - Fast syntax validation"
echo "    • zig_fmt     - Format code"
echo ""
echo "  Project:"
echo "    • zig_version - Check Zig version"
echo "    • zig_init    - Initialize new project"
echo "    • zig_fetch   - Add dependency to build.zig.zon"
echo "    • zig_translate_c - Convert C headers to Zig"
echo ""
echo "  Toolchain (ZVM/ZLS):"
echo "    • zvm_install - Install Zig version with ZLS"
echo "    • zvm_use     - Switch Zig version"
echo "    • zvm_list    - List installed versions"
echo "    • zls_status  - Check ZLS compatibility"
echo ""
echo "Available commands:"
echo "    • /zig-setup  - First-time toolchain setup"
echo "    • /zig-update - Update to latest nightly"
echo "    • /zig-doctor - Diagnose toolchain health"
echo "    • /zig-new    - Create new project"
echo "    • /zig-add    - Add dependency"
echo ""
