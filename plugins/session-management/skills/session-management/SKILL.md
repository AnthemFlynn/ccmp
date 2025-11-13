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

Creates `.sessions/` directory with:
- `config.yaml` - Session configuration (optional)
- `checkpoints/` - Checkpoint storage
- `state.json` - Current session state

### Core Workflows

#### Session Start (`/session-start`)

**Rapid re-immersion for both human and AI**

```bash
/session-start
```

**What happens:**
1. **Project status report generated** - Health, git status, recent work, open items
2. **Context-aware options presented** - AI-guided suggestions based on project state
3. **Branch selection** - Best practice guidance for branch management
4. **Context loaded** - Architecture, decisions, patterns from last session
5. **Session ready** - Both human and AI fully contextualized

**Use when:**
- Starting work on a project
- Returning after days away
- Context switching between projects

#### Create Checkpoint (`/checkpoint`)

**Quick save points during work**

```bash
/checkpoint
```

**What happens:**
1. **Automatic capture** - Git diff, metrics, TDD cycles analyzed
2. **Optional notes** - Add context if desired (press Enter to skip)
3. **Checkpoint saved** - Comprehensive snapshot generated
4. **Git commit** - Optionally create commit with `--commit` flag

**Use when:**
- At logical milestones
- Completing sub-tasks
- Before switching contexts

**Examples:**
```bash
# Simple checkpoint
python scripts/session.py checkpoint --label "oauth-complete"

# Checkpoint with notes and git commit
python scripts/session.py checkpoint --label "feature-complete" --notes "OAuth flow tested" --commit

# With custom commit message
python scripts/session.py checkpoint --label "bugfix" --commit --message "fix: resolve auth token expiry"
```

#### End Session (`/session-end`)

**Comprehensive knowledge capture and handoff**

```bash
/session-end
```

**What happens:**
1. **Session notes prompt** - Capture what you accomplished, decisions, what to remember
2. **Handoff generated** - Full session summary with next steps
3. **Git push** - Optionally push commits to remote (default: yes, use `--no-push` to skip)
4. **State saved** - Ready for next session

**Use when:**
- Finishing work session
- End of day
- Before extended break

## Session Lifecycle

**START** → Load full project context with status report
**WORK** → Track changes automatically in background
**CHECKPOINT** → Save progress with automatic git analysis
**END** → Generate handoff with comprehensive session summary

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

## CCMP Plugin Integration

Session management **automatically integrates** with other CCMP plugins:

### With claude-context-manager 📚
**Auto-loads relevant context on session start:**
```bash
python scripts/session.py start feature/auth
# → Automatically loads src/auth/claude.md
# → Shows context health warnings
# → Includes patterns and gotchas in brief
```

**Checkpoints trigger context health checks:**
```bash
python scripts/session.py checkpoint --label "api-complete"
# → Detects src/api/ changed
# → Warns if context is stale
# → Offers: "Update context? [y/N]"
```

**Handoffs include context health:**
```bash
python scripts/session.py end --handoff
# → Includes context health score
# → Lists files needing updates
# → Recommends maintenance for next session
```

### With tdd-workflow 🧪
**TDD mode automatically enhances sessions:**
```bash
python scripts/session.py start feature/auth --tdd
# → TDD workflow detects and activates
# → Automatic RED-GREEN-REFACTOR checkpoints
# → TDD metrics in session status
# → Test coverage tracking
```

**Session analysis detects TDD:**
```bash
python scripts/session.py analyze
# → Shows TDD cycles completed
# → Detects commits without tests
# → Reports discipline violations
```

### Integration API
Uses `.ccmp/state.json` for plugin coordination. See `lib/ccmp_integration.py` for details.

**Developers:** Import the integration library:
```python
from lib.ccmp_integration import CCMPIntegration

integration = CCMPIntegration()
if integration.is_active("session-management"):
    session = integration.get_state("session-management")
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
