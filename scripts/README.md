# Development Scripts

Quick reload scripts for CCMP marketplace development.

## Scripts

### 🚀 `reload-local.sh` (Fastest - Recommended for Dev)

Uses your **local working directory** - no git push needed!

```bash
./scripts/reload-local.sh
```

**When to use:**
- During active development
- Testing changes before commit
- Rapid iteration

**Speed:** ~5 seconds

---

### 🔄 `reload-marketplace.sh` (Production Test)

Uses **GitHub** - requires `git push` first!

```bash
./scripts/reload-marketplace.sh
```

**When to use:**
- Testing what users will get
- After git push to verify live version
- Final validation before release

**Speed:** ~15 seconds (network dependent)

---

## Workflow

### Development Cycle

```bash
# 1. Make changes to plugin.json or SKILL.md files
vim plugins/workflow-suite/.claude-plugin/plugin.json

# 2. Reload local immediately (no commit needed)
./scripts/reload-local.sh

# 3. Test in Claude Code
# "What skills do I have available?"

# 4. Iterate until it works
# (repeat steps 1-3)

# 5. Once working, commit and test from GitHub
git add -A && git commit -m "fix: description" && git push
./scripts/reload-marketplace.sh
```

### Quick Fixes

```bash
# Fix something
vim plugins/workflow-suite/skills/session-management/SKILL.md

# Reload immediately
./scripts/reload-local.sh

# Test
# No commit needed yet!
```

---

## Hot Reload?

**Claude Code doesn't support hot reload** - you must remove and reinstall plugins after changes.

These scripts automate that process:
- Remove all old plugins
- Refresh marketplace
- Reinstall fresh
- Verify installation

---

## Troubleshooting

### Check Installation Errors

In Claude Code: **"View installation status (errors)"**

### Manual Commands

```bash
# List installed plugins
claude-code plugin list

# List marketplaces
claude-code marketplace list

# Remove specific plugin
claude-code plugin remove workflow-suite

# Check plugin directory
ls -la ~/.claude/plugins/marketplaces/ccmp/
```

### Common Issues

**"Plugin not found"**
- Plugin name is wrong (use `claude-code plugin list`)
- Run with correct name from list

**"Validation errors"**
- Check `plugin.json` has no invalid fields
- Run `./scripts/reload-local.sh` to test local changes

**Skills not appearing**
- Ensure `skills/` directory exists at plugin root
- Check `SKILL.md` files have proper frontmatter
- Verify no `category` or `skills` array in plugin.json

---

## Files

- `reload-local.sh` - Fast local development reload
- `reload-marketplace.sh` - GitHub production test reload
- `README.md` - This file
