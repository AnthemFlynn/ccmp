#!/bin/bash
# Quick reload script for CCMP marketplace during development

set -e  # Exit on error

echo "🔄 Reloading CCMP marketplace and plugins..."
echo ""

# Remove all CCMP plugins (ignore errors if not installed)
echo "📦 Removing old plugins..."
claude plugin remove workflow-suite 2>/dev/null || true
claude plugin remove session-management 2>/dev/null || true
claude plugin remove claude-context-manager 2>/dev/null || true
claude plugin remove tdd-workflow 2>/dev/null || true
echo "✅ Old plugins removed"
echo ""

# Remove and re-add marketplace to force refresh
echo "🏪 Refreshing marketplace..."
claude marketplace remove ccmp 2>/dev/null || true
claude marketplace add AnthemFlynn/ccmp
echo "✅ Marketplace refreshed"
echo ""

# Install workflow-suite (bundles all three skills)
echo "📥 Installing workflow-suite..."
claude plugin add AnthemFlynn/ccmp/workflow-suite
echo "✅ workflow-suite installed"
echo ""

# Check for errors
echo "🔍 Checking installation status..."
claude plugin list
echo ""

echo "✨ Done! Check 'View installation status (errors)' in Claude Code to verify."
echo ""
echo "Test in Claude Code with: 'What skills do I have available?'"
