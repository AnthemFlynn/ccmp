---
name: session-management
description: Git-native session lifecycle management for software development. Use when starting/resuming coding sessions, creating checkpoints, tracking objectives and blockers, generating handoffs between sessions, or needing context preservation across work sessions. Provides intelligent onboarding for AI coding agents by loading comprehensive project context.
---

# Session Management

Manage coding sessions with git-native workflows, intelligent context preservation, and seamless agent onboarding.

## Core Concept

**Sessions = Branches + Context**

Session management enhances git workflows by:
- Mapping branches to work sessions with objectives
- Creating enhanced commits with decision metadata
- Tracking progress, blockers, and architectural decisions
- Generating comprehensive handoffs between sessions
- Providing instant context loading for AI agents

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

# With architectural decision
python scripts/session.py checkpoint --decision "Using JWT over sessions for stateless auth"
```

### End Session

```bash
python scripts/session.py end --handoff
```

Generates handoff document with:
- Completed objectives
- Decisions made
- Active blockers
- Progress metrics
- Next steps

## Session Lifecycle

**START** → Load context, set objectives, brief agent  
**WORK** → Track changes, record decisions  
**CHECKPOINT** → Save progress, update metrics  
**END** → Generate handoff, archive session

## Key Features

### 1. Objectives Management

Track what you're trying to accomplish:

```bash
# Add objective
python scripts/session.py objectives add "Implement OAuth2 integration"

# Mark complete
python scripts/session.py objectives complete obj-1

# List all
python scripts/session.py objectives list
```

### 2. Blocker Tracking

Record impediments:

```bash
# Add blocker
python scripts/session.py blockers add "Waiting on API keys"

# Resolve
python scripts/session.py blockers resolve blk-1
```

### 3. Decision Logging

Capture architectural decisions with context:

```bash
# Record decision
python scripts/session.py decisions add "Using repository pattern for data access" \
  --rationale "Separates domain logic from persistence" \
  --alternatives "Active Record: Too coupled to database"
```

### 4. Context Queries

Check current state:

```bash
# Full status
python scripts/session.py status

# Just objectives
python scripts/session.py status --objectives

# History
python scripts/session.py history --count 10
```

## Agent Onboarding

When AI agents (like Claude Code) start, session management provides instant context:

```python
# Automatically loads on agent start:
# - Project architecture pattern
# - Code conventions
# - Recent decisions
# - Current objectives
# - Active blockers
# - Git history analysis
# - File changes summary
```

Agent receives structured brief including:
- What we're building (objectives)
- How to build it (architecture, patterns, conventions)
- What's done (progress)
- What's next (next actions)
- What to watch for (blockers, TODOs)

## Storage Structure

```
project/
├── .session/                # Git-tracked, shared across team
│   ├── config.yaml         # Configuration
│   ├── architecture.md     # Architecture documentation
│   ├── conventions.md      # Code conventions
│   └── decision-log.md     # All decisions (auto-generated)
│
└── .git/
    └── sessions/           # Local, developer-specific
        └── <branch>/
            ├── objectives.md
            ├── blockers.md
            └── context.json
```

**Design principle**: Shared context (architecture, conventions) is git-tracked. Personal workflow data (objectives, notes) stays local.

## Configuration

Edit `.session/config.yaml`:

```yaml
session:
  auto_track: true          # Track file changes automatically
  handoff_on_end: true      # Generate handoff when ending
  
context:
  architecture: hexagonal   # Your architecture pattern
  patterns:                 # Patterns to enforce
    - repository-pattern
    - dependency-injection
  
tracking:
  watch_patterns:           # Files to monitor
    - "src/**/*.py"
    - "tests/**/*.py"
```

## Workflows

### Daily Development

```bash
# Morning: Resume work
python scripts/session.py resume

# During work: Checkpoint at milestones
python scripts/session.py checkpoint --label "api-complete"

# Evening: End with handoff
python scripts/session.py end
```

### Context Switching

```bash
# Urgent bug comes in
python scripts/session.py switch hotfix/critical-bug

# Fix bug
python scripts/session.py checkpoint --message "Fix security issue"
python scripts/session.py end --merge-to main

# Back to feature
python scripts/session.py resume feature/main-work
```

### Team Handoffs

```bash
# Generate comprehensive handoff
python scripts/session.py end --handoff --summary

# Next developer loads context
python scripts/session.py resume <branch>
```

## Enhanced Commits

Session checkpoints create git commits with rich metadata:

```
feat(auth): Implement OAuth2 provider

Completed Google OAuth flow with PKCE support.

Session-Objectives:
- [x] OAuth provider interface
- [▶] Google OAuth (this commit)
- [ ] GitHub OAuth (next)

Decisions:
- Using PKCE flow for enhanced security
  Rationale: Protection against code interception
  
Impact:
- Added: src/auth/oauth_provider.py
- Tests: +12 unit tests
- Coverage: 79% → 84%

Session-Time: 2h 15m
```

## Advanced Features

### Session Analysis

```bash
# Analyze session health
python scripts/session.py analyze

# Calculate velocity
python scripts/session.py analyze --velocity

# Pattern detection
python scripts/session.py analyze --patterns
```

### Session History

```bash
# Recent sessions with metrics
python scripts/session.py history --count 5 --metrics

# Compare sessions
python scripts/session.py compare <session-id>
```

### Reports

```bash
# Weekly summary
python scripts/session.py report --weekly

# Project summary
python scripts/session.py report --project --format markdown
```

## Bundled Resources

### Scripts

- **`init_session.py`** - Initialize session management in project
- **`session.py`** - Main CLI for all session operations
- **`analyze_git.py`** - Git history analysis utilities

### References

- **`commands.md`** - Complete command reference
- **`handoff-template.md`** - Template for session handoffs
- **`config-reference.md`** - All configuration options

### Assets

- **`config-template.yaml`** - Default configuration
- **`architecture-template.md`** - Architecture documentation template
- **`conventions-template.md`** - Conventions template

## Best Practices

**For Solo Development:**
- Start every session with objectives
- Checkpoint at logical milestones
- Record decisions when making them
- End sessions with handoffs (helps future you)

**For Teams:**
- Commit `.session/` directory (shared context)
- Keep personal workflow local
- Link blockers to issue tracker
- Generate handoffs for transitions

**For AI-Assisted Development:**
- Session management provides instant agent context
- No need to re-explain project structure
- Architectural patterns automatically enforced
- Decisions preserved across sessions

## Troubleshooting

**Session not loading?**
```bash
python scripts/session.py status --verbose
python scripts/session.py start --resume
```

**Need to reinitialize?**
```bash
python scripts/init_session.py --force
```

**View current configuration:**
```bash
cat .session/config.yaml
```

## Integration Notes

Session management is designed to work with:
- **Git** (required) - Source of truth for history
- **Issue Trackers** (optional) - Link blockers to tickets  
- **CI/CD** (optional) - Include build status in briefings
- **Coverage Tools** (optional) - Track quality metrics

For integration guides, see `references/integrations.md`.

## See Also

- **Full command reference**: See `references/commands.md`
- **Configuration options**: See `references/config-reference.md`
- **Handoff format**: See `references/handoff-template.md`
- **Integration guides**: See `references/integrations.md`
