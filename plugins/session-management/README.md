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

## Usage

### Starting a Session

```bash
# Via slash command
/session-management:session-start

# Via CLI
python3 scripts/session.py start --branch feature/my-feature --objective "Implement user authentication"
```

**What happens:**
1. Generates project status report (if project-status-report installed)
2. Presents context-aware options (resume existing work, start new, address health issues)
3. Checks out or creates the branch
4. Saves session state with objectives
5. Updates plugin coordination state

### Creating Checkpoints

```bash
# Via slash command
/session-management:checkpoint --commit --notes "Completed OAuth flow"

# Via CLI
python3 scripts/session.py checkpoint --label "oauth-complete" --commit --notes "Implemented OAuth2 authentication"
```

**What happens:**
1. Captures current git diff and changes
2. Analyzes changes with git-commit skill (if installed)
3. Generates professional commit message
4. Creates checkpoint document in `.sessions/checkpoints/`
5. Optionally creates git commit with generated message

### Ending a Session

```bash
# Via slash command
/session-management:session-end

# Via CLI
python3 scripts/session.py end --push
```

**What happens:**
1. Prompts for session summary (accomplished, decisions, remember)
2. Generates comprehensive handoff document
3. Saves handoff to `.sessions/handoffs/`
4. Optionally pushes commits to remote (with confirmation)
5. Updates session state to "completed"

### Checking Session Status

```bash
python3 scripts/session.py status
```

**Shows:**
- Current session details (branch, objectives, start time)
- Session mode (TDD, regular)
- Recent checkpoints
- Integration state (TDD cycles, context health)

## Examples

### Example 1: Start a New Feature Session

```bash
# Start session with Claude
/session-management:session-start

# Output:
# === PROJECT STATUS REPORT ===
#
# ✅ Tests: 24 passed, 0 failed
# ✅ Build: Success
# ⚠️  3 uncommitted changes
#
# What would you like to work on?
# 1. Resume existing work
# 2. Start new work
# 3. Address health issues first
#
# Choice [1/2/3]: 2

# Enter new branch name: feature/oauth-integration
# Enter objectives (one per line, empty line to finish):
# > Implement OAuth2 authentication with Google and GitHub
# > Add token refresh mechanism
# >

# ✅ Session started on feature/oauth-integration
# Objectives:
# - Implement OAuth2 authentication with Google and GitHub
# - Add token refresh mechanism
```

### Example 2: Create a Checkpoint with Auto-Commit

```bash
# Work on your code, then create checkpoint
/session-management:checkpoint --commit --notes "Implemented OAuth2 flow with token refresh"

# Output:
# 📊 Analyzed changes: feat (100% confidence)
# 📝 Suggested commit:
#    feat(auth): add OAuth2 authentication
#
# Implemented OAuth2 flow with token refresh
#
# ✅ Checkpoint created: 2025-11-15T14-30-00
# 📝 Git commit created
# 💾 Saved to .sessions/checkpoints/
```

### Example 3: End Session with Handoff

```bash
/session-management:session-end

# Prompts:
# What did you accomplish?
# > Completed OAuth2 authentication system with Google and GitHub providers
#
# Key decisions made?
# > Using RS256 for JWT signing, 24h token expiry, 30d refresh token expiry
#
# What to remember for next session?
# > Need to add integration tests for OAuth edge cases

# Output:
# ✅ Session ended. Handoff generated.
# 📄 Handoff saved to .sessions/handoffs/handoff_2025-11-15T16-30-00.md
#
# Commits to push: 3
# - feat(auth): add OAuth2 authentication
# - feat(auth): implement token refresh
# - docs(auth): update API documentation
#
# Push 3 commits to remote? [Y/n]: y
# 📤 Pushed to remote
```

### Example 4: Resume Previous Session

```bash
/session-management:session-start

# Output:
# Last session was on branch: feature/oauth-integration
# Resume 'feature/oauth-integration'? [Y/n]: y
#
# ✅ Switched to branch: feature/oauth-integration
# 📖 Loading session context...
#
# Session Objectives:
# ✓ Implement OAuth2 authentication with Google and GitHub
# ✓ Add token refresh mechanism
# ○ Write integration tests
#
# Last Checkpoint: 19 hours ago
# Status: GREEN (all tests passing)
# Next: Add integration tests for OAuth edge cases
```

### Example 5: Integration with TDD Workflow

When using with tdd-workflow plugin:

```bash
# Start session in TDD mode
python3 scripts/session.py start --branch feature/validation --tdd

# Work using RED-GREEN-REFACTOR...

# Create checkpoint at GREEN phase
/session-management:checkpoint --commit --tdd-phase GREEN

# Session automatically tracks:
# - TDD cycles completed
# - Test pass/fail history
# - Time in each phase
# - Discipline adherence
```

### Example 6: Checkpoint History

```bash
# View recent checkpoints
python3 scripts/session.py history --limit 5

# Output:
# === CHECKPOINT HISTORY ===
#
# 2025-11-15T16:30:00 - OAUTH_COMPLETE
# Status: GREEN (tests passing)
# Changes: +245 lines, -12 lines (3 files)
# Commit: feat(auth): add OAuth2 authentication
#
# 2025-11-15T14:20:00 - TOKEN_REFRESH
# Status: GREEN
# Changes: +89 lines, -5 lines (2 files)
# Commit: feat(auth): implement token refresh
#
# 2025-11-15T12:15:00 - OAUTH_PROVIDERS
# Status: RED (2 tests failing)
# Changes: +156 lines (4 files)
# Note: Implementing OAuth provider interfaces
```

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
