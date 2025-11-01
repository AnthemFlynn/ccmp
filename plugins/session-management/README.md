# Session Management

Git-native session lifecycle management with context preservation, checkpoint tracking, and seamless handoffs between coding sessions.

## Description

Manage coding sessions with git-native workflows, intelligent context preservation, and seamless agent onboarding.

## Core Concept

**Sessions = Branches + Context**

Session management enhances git workflows by:
- Mapping branches to work sessions with objectives
- Creating enhanced commits with decision metadata
- Tracking progress, blockers, and architectural decisions
- Generating comprehensive handoffs between sessions
- Providing instant context loading for AI agents

## Installation

### From Marketplace

```bash
claude-code plugin add AnthemFlynn/ccmp/session-management
```

### Manual Installation

1. Clone this repository
2. Copy `plugins/session-management` to your Claude Code plugins directory
3. Restart Claude Code

## Quick Start

### Initialize in Project

```bash
python scripts/init_session.py
```

Creates `.session/` directory with:
- `config.yaml` - Session configuration
- `architecture.md` - Project architecture (edit for your project)
- `conventions.md` - Code conventions (edit for your project)

### Start a Session

```bash
# New feature session
python scripts/session.py start feature/new-feature --objective "Build user authentication"

# Resume existing
python scripts/session.py resume
```

### Create Checkpoints

```bash
# Save progress
python scripts/session.py checkpoint --label "oauth-complete"
```

## Features

- Git-native workflows (branches = sessions)
- Context preservation across sessions
- Checkpoint tracking with labels
- Architectural decision recording
- Comprehensive session handoffs
- AI agent onboarding

## License

MIT
