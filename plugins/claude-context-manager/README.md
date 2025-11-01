# Claude Context Manager

Autonomous context management for codebases through `claude.md` files with monitoring, staleness detection, and intelligent updates.

## Description

This plugin enables Claude to work as an autonomous **context manager** for codebases, maintaining accurate and actionable context intelligence through `claude.md` files.

## Features

- **Behavioral guidance**: Instructions for working proactively as a context manager
- **Monitoring tools**: Scripts to assess context health and detect staleness
- **Update automation**: Intelligent context synchronization based on code changes
- **Quality standards**: Patterns for creating actionable, dense agent context

## Installation

### From Marketplace

```bash
claude-code plugin add AnthemFlynn/ccmp/claude-context-manager
```

### Manual Installation

1. Clone this repository
2. Copy `plugins/claude-context-manager` to your Claude Code plugins directory
3. Restart Claude Code

## Usage

The skill provides four main workflows:

1. **Initial Setup** - First time working in a repository
2. **Continuous Maintenance** - Working in active codebase
3. **Change-Responsive Update** - After significant code changes
4. **Context Exploration** - Exploring existing context

See the full skill documentation in `skills/claude-context-manager/SKILL.md` for detailed instructions.

## Core Concept

`claude.md` files are **cognitive maps** - operational intelligence that helps Claude:
- Navigate faster (know structure and entry points)
- Generate better (follow existing patterns)
- Avoid errors (understand constraints and gotchas)
- Make decisions (know the rules and conventions)

This is **agent context**, not documentation. The goal is making future-Claude more effective.

## License

MIT
