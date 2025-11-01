# Anthem's Claude Code Marketplace (CCMP)

A curated collection of skills and plugins for Claude Code, featuring tools for context management, session workflows, and productivity enhancements.

## 🚀 Quick Start

### Adding Plugins from This Marketplace

```bash
# Add the marketplace to your Claude Code configuration
claude-code marketplace add AnthemFlynn/ccmp

# Install a plugin
claude-code plugin add AnthemFlynn/ccmp/claude-context-manager
claude-code plugin add AnthemFlynn/ccmp/session-management
```

### Manual Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/AnthemFlynn/ccmp.git
   ```

2. Copy desired plugins to your Claude Code plugins directory:
   ```bash
   cp -r ccmp/plugins/claude-context-manager ~/.claude/plugins/
   ```

3. Restart Claude Code

## 📦 Available Plugins

### ⭐ Claude Context Manager

**Category:** Productivity
**Version:** 1.0.0

Autonomous context management for codebases through `claude.md` files with monitoring, staleness detection, and intelligent updates.

**Features:**
- Behavioral guidance for proactive context management
- Monitoring tools for context health assessment
- Automated context synchronization
- Quality standards for actionable agent context

[View Documentation](./plugins/claude-context-manager/README.md)

---

### ⭐ Session Management

**Category:** Productivity
**Version:** 1.0.0

Git-native session lifecycle management with context preservation, checkpoint tracking, and seamless handoffs between coding sessions.

**Features:**
- Git-native workflows (branches = sessions)
- Context preservation across sessions
- Checkpoint tracking with labels
- Architectural decision recording
- AI agent onboarding

[View Documentation](./plugins/session-management/README.md)

---

## 🛠️ For Plugin Developers

### Repository Structure

```
ccmp/
├── .claude-plugin/
│   ├── marketplace.extended.json    # Source of truth (edit this)
│   └── marketplace.json              # Auto-generated (don't edit)
├── plugins/
│   ├── claude-context-manager/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── skills/
│   │   │   └── claude-context-manager/
│   │   │       └── SKILL.md
│   │   └── README.md
│   └── session-management/
│       └── ...
├── scripts/
│   └── sync-marketplace.js
├── package.json
└── README.md
```

### Adding a New Plugin

1. **Create plugin structure:**
   ```bash
   mkdir -p plugins/your-plugin/.claude-plugin
   mkdir -p plugins/your-plugin/skills/your-skill
   ```

2. **Add plugin metadata** (`plugins/your-plugin/.claude-plugin/plugin.json`):
   ```json
   {
     "name": "your-plugin",
     "version": "1.0.0",
     "description": "Your plugin description",
     "author": {
       "name": "Your Name",
       "email": "AnthemFlynn@users.noreply.github.com"
     },
     "category": "productivity",
     "keywords": ["keyword1", "keyword2"],
     "skills": [
       {
         "name": "your-skill",
         "path": "./skills/your-skill/SKILL.md",
         "description": "Skill description"
       }
     ]
   }
   ```

3. **Add to marketplace catalog** (`.claude-plugin/marketplace.extended.json`):
   ```json
   {
     "name": "your-plugin",
     "source": "./plugins/your-plugin",
     "description": "Your plugin description",
     "version": "1.0.0",
     "category": "productivity",
     "keywords": ["keyword1", "keyword2"],
     "author": {
       "name": "Your Name",
       "email": "AnthemFlynn@users.noreply.github.com"
     },
     "featured": false
   }
   ```

4. **Sync the marketplace:**
   ```bash
   npm run sync
   ```

5. **Test and commit:**
   ```bash
   git add .
   git commit -m "feat: Add your-plugin"
   ```

### Syncing the Marketplace

The marketplace uses a two-catalog system:

- **`marketplace.extended.json`** - Source of truth with full metadata (edit this)
- **`marketplace.json`** - Auto-generated CLI-compatible version (don't edit)

To sync after making changes:

```bash
npm run sync
```

This removes extended fields (`featured`, `mcpTools`, etc.) from `marketplace.json`.

## 📋 Valid Categories

- `productivity`
- `security`
- `testing`
- `deployment`
- `documentation`
- `analysis`
- `integration`
- `ai`
- `devops`
- `debugging`
- `code-quality`
- `design`
- `api-development`
- `database`
- `performance`

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-plugin`)
3. Add your plugin following the structure above
4. Run `npm run sync` to update the catalog
5. Commit your changes (`git commit -m 'feat: Add amazing-plugin'`)
6. Push to the branch (`git push origin feature/amazing-plugin`)
7. Open a Pull Request

### Contribution Guidelines

- Plugins must include a `README.md` with installation and usage instructions
- Skills must have a `SKILL.md` file with clear documentation
- Follow semantic versioning (x.y.z)
- Include at least 2 keywords for discoverability
- Test your plugin before submitting

## 📄 License

MIT License - See individual plugin directories for specific licenses.

## 🙋 Support

- **Issues:** [GitHub Issues](https://github.com/AnthemFlynn/ccmp/issues)
- **Discussions:** [GitHub Discussions](https://github.com/AnthemFlynn/ccmp/discussions)

---

**Maintained by AnthemFlynn** • [GitHub](https://github.com/AnthemFlynn) • [Email](AnthemFlynn@users.noreply.github.com)
