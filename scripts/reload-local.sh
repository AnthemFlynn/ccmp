#!/bin/bash
# Fast local reload for development (doesn't require git push)

set -e

echo "🚀 Fast local reload (development mode)..."
echo ""

# Remove old plugins
echo "📦 Removing old plugins..."
claude plugin remove workflow-suite 2>/dev/null || true
claude plugin remove session-management 2>/dev/null || true
claude plugin remove claude-context-manager 2>/dev/null || true
claude plugin remove tdd-workflow 2>/dev/null || true
echo "✅ Removed"
echo ""

# Remove marketplace
echo "🏪 Removing marketplace..."
claude marketplace remove ccmp 2>/dev/null || true
echo "✅ Removed"
echo ""

# Add marketplace from local directory
echo "📁 Adding marketplace from local files..."
claude marketplace add /Users/dblspeak/projects/skills
echo "✅ Local marketplace added"
echo ""

# Install workflow-suite from local
echo "📥 Installing workflow-suite from local..."
claude plugin add ccmp/workflow-suite
echo "✅ Installed"
echo ""

# Show status
echo "🔍 Plugin status:"
claude plugin list
echo ""

echo "✨ Done! Local files are now active."
echo "💡 No git push needed - uses your working directory"
echo ""
echo "Test: 'What skills do I have available?'"
