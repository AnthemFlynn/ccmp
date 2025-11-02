# Session Management Skill

A complete, production-ready skill for git-native session lifecycle management in software development.

## What You Got

You have a proper `.skill` file that can be installed in Claude:

**`session-management.skill`** - A complete skill package containing:
- SKILL.md with comprehensive instructions
- Python scripts for session management
- Reference documentation
- Configuration and template files

## Installation

### For Claude Desktop

1. Locate your Claude skills directory:
   - **macOS**: `~/Library/Application Support/Claude/skills/`
   - **Windows**: `%APPDATA%\Claude\skills\`
   - **Linux**: `~/.config/Claude/skills/`

2. Copy the `.skill` file to the skills directory:
   ```bash
   cp session-management.skill ~/Library/Application\ Support/Claude/skills/
   ```

3. Restart Claude or reload skills

The skill will automatically be available in Claude conversations.

## What This Skill Does

Session Management provides git-native session lifecycle management for coding:

**Core Features:**
- Start/resume coding sessions with full context
- Create checkpoints with enhanced commits
- Track objectives, blockers, and decisions
- Generate comprehensive handoffs between sessions
- Provide instant context loading for AI agents

**When Claude Uses This:**
- When you start/resume coding sessions
- When creating checkpoints during work
- When tracking progress, objectives, or blockers
- When generating handoffs between sessions
- When AI agents need project context

## Quick Start (After Installation)

Once installed, you can ask Claude things like:

```
"Help me set up session management in my project"

"Start a new session for feature/user-auth with objective: implement JWT authentication"

"Create a checkpoint labeled 'oauth-complete'"

"Show me the current session status"

"End this session and generate a handoff"
```

Claude will use the skill automatically and guide you through the process.

## What's Included in the Skill

### Scripts (`scripts/`)
- **init_session.py** - Initialize session management in a project
- **session.py** - Main CLI for all session operations

### References (`references/`)
- **commands.md** - Complete command reference
- **config-reference.md** - All configuration options
- **handoff-template.md** - Template for session handoffs

### Assets (`assets/`)
- **config-template.yaml** - Default configuration template
- **architecture-template.md** - Architecture documentation template
- **conventions-template.md** - Code conventions template

## Key Concepts

**Sessions = Branches + Context**

The skill enhances git workflows by:
- Mapping branches to work sessions with objectives
- Creating enhanced commits with decision metadata
- Tracking progress, blockers, and architectural decisions
- Generating comprehensive handoffs between sessions
- Providing instant context loading for AI agents

## Storage Structure

When initialized in a project:

```
your-project/
├── .session/                # Git-tracked, shared
│   ├── config.yaml         # Configuration
│   ├── architecture.md     # Architecture docs
│   └── conventions.md      # Code conventions
│
└── .git/
    └── sessions/           # Local, not tracked
        └── <branch>/
            ├── objectives.md
            ├── blockers.md
            └── context.json
```

## Generic & Universal

This skill is completely generic and not tied to any specific:
- Architecture pattern (works with any)
- Programming language (language-agnostic)
- Team or workflow (adapts to yours)
- Project type (any software project)

You customize it by editing the `.session/` configuration files in your project.

## Technical Details

**Implementation**: Python 3.7+
**Dependencies**: Git (required), standard library only
**Platform**: Cross-platform (Linux, macOS, Windows)

**Skill Type**: Workflow & Tool Integration
**Progressive Disclosure**: SKILL.md (core), references/ (detailed), scripts/ (executable)

## Next Steps

1. **Install the skill** in Claude (see Installation above)
2. **Try it out**: Ask Claude to help you initialize session management
3. **Customize**: Edit `.session/config.yaml` for your project
4. **Use it**: Start your first session and see how it works

## Validation

This skill was created following the official Claude skill-creator patterns:
- ✅ Proper YAML frontmatter
- ✅ Concise SKILL.md (under 500 lines)
- ✅ Progressive disclosure with bundled resources
- ✅ Generic and universal design
- ✅ Validated and packaged with official tools

## Support

The skill includes comprehensive documentation:
- Read SKILL.md for core instructions
- Check references/commands.md for all commands
- See references/config-reference.md for configuration
- Review references/handoff-template.md for handoff format

---

**Skill Package**: `session-management.skill`
**Version**: 1.0.0
**Format**: Standard Claude skill package (.skill is a zip file)

Ready to transform your development workflow!
