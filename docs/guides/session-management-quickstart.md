# Session Management Quick Start

Get started with git-native session management in 5 minutes.

## Overview

Session management provides three core workflows:
1. **Session Start** - Rapid re-immersion with project status report
2. **Checkpoint** - Quick save points during work
3. **Session End** - Comprehensive handoff generation

## Installation

Install the plugins via Claude Code:

```bash
claude plugin install project-status-report
claude plugin install session-management
```

Or manually link from this repository:

```bash
# From the skills repository root
claude plugin link plugins/project-status-report
claude plugin link plugins/session-management
```

## Initialize in Your Project

Navigate to your project and initialize session management:

```bash
cd your-project
python3 -c "from pathlib import Path; import sys; sys.path.insert(0, str(Path('~/.claude/plugins/session-management/skills/session-management/scripts').expanduser())); from init_session import main; main()"
```

Or if you have the scripts locally:

```bash
python3 /path/to/skills/plugins/session-management/skills/session-management/scripts/init_session.py
```

This creates the `.session/` and `.sessions/` directory structure.

## Your First Session

### 1. Start Session

Use the slash command in Claude Code:

```
/session-start
```

Or run directly:

```bash
python3 scripts/session.py start my-feature --objective "Implement user authentication"
```

You'll see:
- Project health report (tests, coverage, build status)
- Git status (branch, commits, sync)
- Recent session summary (if available)
- Options for what to work on

The system will:
- Present context-aware options
- Guide branch selection
- Set up session objectives
- Load full project context

### 2. Do Work

Work normally using your development workflow. Session management observes in the background through:
- Git operations
- File changes
- Test results

### 3. Create Checkpoints

Create checkpoints at logical milestones:

```
/checkpoint
```

Or:

```bash
python3 scripts/checkpoint.py --label "completed authentication module"
```

Quick save point that captures:
- Git diff analysis (what changed)
- Recent commits
- TDD metrics (if available)
- Optional notes

Add the `--commit` flag to create a git commit:

```bash
python3 scripts/checkpoint.py --label "auth module" --commit
```

### 4. End Session

End your session with comprehensive handoff:

```
/session-end
```

Or:

```bash
python3 scripts/session.py end
```

You'll be prompted for:
- What did you accomplish?
- Key decisions made?
- What to remember for next session?

The system generates a handoff document with:
- Session summary
- Files changed
- Objectives completed
- Next steps

## Next Session

Start your next session with:

```
/session-start
```

Your previous handoff is automatically loaded, showing:
- What you accomplished last time
- Where you left off
- Open objectives
- Suggested next actions

## Key Commands

### Project Status Report (Anytime)

```
/project-report
```

Get quick project overview without session overhead:
- Health indicators
- Git status
- Open work items
- Suggested next actions

### Session Commands

```
/session-start         # Start or resume session
/checkpoint           # Create checkpoint
/session-end          # End session with handoff
```

### Direct Python Access

```bash
# Initialize session management
python3 scripts/init_session.py

# Generate project report
python3 scripts/report.py

# Start session
python3 scripts/session.py start <branch> --objective "..."

# Create checkpoint
python3 scripts/checkpoint.py --label "milestone" [--commit]

# End session
python3 scripts/session.py end [--push]

# Generate handoff
python3 scripts/handoff.py --notes "Session summary"
```

## Best Practices

### 1. Start Every Session
- Get full context before deciding what to work on
- Review health indicators
- Check git status
- Load recent work

### 2. Checkpoint at Milestones
- When completing a sub-task
- Before switching contexts
- After significant changes
- Not after every tiny change (use git commits for that)

### 3. End with Good Notes
- Be specific about what you accomplished
- Document key decisions
- Note what to remember for next time
- Future you will thank current you

### 4. Use Project Report Mid-Session
- Quick health check without session overhead
- See current git status
- Review open work items
- No need to end current session

## Directory Structure

```
your-project/
├── .session/              # Session configuration (legacy)
│   ├── config.yaml       # Session settings
│   ├── architecture.md   # Project architecture
│   └── conventions.md    # Code conventions
├── .sessions/            # Session state and checkpoints
│   ├── state.json       # Current session state
│   └── checkpoints/     # Checkpoint and handoff documents
│       ├── 2025-11-12T14-30-00.md
│       └── 2025-11-12T17-45-00-HANDOFF.md
└── .git/
    └── sessions/         # Git-backed session data (future)
```

## Integration with Other Tools

### TDD Workflow
Session management integrates with TDD workflow to capture:
- TDD cycles completed
- Current phase (RED/GREEN/REFACTOR)
- Discipline score

### Context Manager
Reads context health from `.ccmp/state.json` if available:
- Context health score
- Critical files needing attention

### Superpowers
Session management is designed as an observer:
- Doesn't interrupt your workflow
- Captures data passively
- Presents insights at session boundaries

## Troubleshooting

### Session not starting?
- Ensure `.session/` or `.sessions/` directory exists
- Run `init_session.py` first
- Check you're in a git repository

### Report not showing?
- `project-status-report` plugin must be installed
- Falls back gracefully if not available
- Check plugin installation: `claude plugin list`

### Git operations failing?
- Ensure you're in a git repository
- Check remote is configured for push operations
- Verify git credentials are set up

### Checkpoint not saving?
- Ensure `.sessions/checkpoints/` directory exists
- Check write permissions
- Verify git diff is working

### Handoff shows "Unknown" branch?
- Expected when running handoff.py directly
- Use `session.py start` to initialize session state
- Or manually create `.sessions/state.json`

## Advanced Usage

### Programmatic Access

```python
from checkpoint import CheckpointManager
from handoff import HandoffGenerator
from report import ReportGenerator

# Generate project report
generator = ReportGenerator()
report = generator.generate()
print(report)

# Create checkpoint
manager = CheckpointManager()
checkpoint = manager.generate_checkpoint(
    notes="Completed authentication module",
    label="auth-complete"
)

# Generate handoff
handoff_gen = HandoffGenerator()
handoff = handoff_gen.generate_handoff(
    session_notes="Successfully implemented user auth with JWT tokens"
)
```

### Custom Integration

Session management uses observer pattern and can integrate with:
- CI/CD pipelines
- Project management tools
- Team communication tools
- Analytics platforms

State is stored in standard formats:
- JSON for machine-readable state
- Markdown for human-readable documents

## What's Next?

1. **Customize** `.session/architecture.md` and `.session/conventions.md` for your project
2. **Integrate** with your existing workflow
3. **Experiment** with checkpoint frequency to find what works for you
4. **Share** handoff documents with team members for knowledge transfer

## Getting Help

- View SKILL.md in each plugin for detailed documentation
- Check examples in `docs/guides/`
- Review implementation plans in `docs/plans/`
- Open issues for bugs or feature requests

## Philosophy

Session management minimizes context-switching time by:
- **Rapid re-immersion**: < 2 minutes to full context
- **Automatic capture**: No required input for checkpoints
- **Git-native**: Leverages existing git workflow
- **Standalone**: Works without other plugins
- **Observer pattern**: Doesn't interrupt your flow

Start every session with full context. End every session with complete handoff.
