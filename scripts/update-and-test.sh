#!/bin/bash
# Update marketplace and reinstall workflow-suite with fresh version

set -e

echo "🔄 Updating CCMP marketplace to latest version..."
echo ""

# Update marketplace from GitHub
echo "📡 Fetching latest from GitHub..."
claude plugin marketplace update ccmp
echo "✅ Marketplace updated"
echo ""

# Remove old installation
echo "🗑️  Removing old workflow-suite installation..."
claude plugin uninstall workflow-suite 2>/dev/null || true
claude plugin uninstall session-management 2>/dev/null || true
claude plugin uninstall claude-context-manager 2>/dev/null || true
claude plugin uninstall tdd-workflow 2>/dev/null || true
echo "✅ Old installations removed"
echo ""

# Fresh install
echo "📥 Installing fresh workflow-suite..."
claude plugin install workflow-suite@ccmp
echo "✅ workflow-suite installed"
echo ""

# Verify installation
echo "🔍 Checking installation status..."
echo ""
echo "Installed plugins:"
claude plugin marketplace list
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✨ Done! Now:"
echo ""
echo "1. RESTART Claude Code (important for skill discovery)"
echo "2. Check 'View installation status (errors)'"
echo "   - Should see NO errors for workflow-suite"
echo ""
echo "3. Test in a conversation:"
echo "   'What skills do I have available?'"
echo ""
echo "   Expected: claude-context-manager, session-management, tdd-workflow"
echo ""
echo "4. Test actual usage:"
echo "   'Initialize session management in my project'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
