# Session Management Command Reference

Complete reference for all session management commands.

## Session Lifecycle Commands

### `start` - Start New Session

```bash
python scripts/session.py start <branch-name> [options]
```

**Options:**
- `--objective "text"` - Set primary objective for this session
- `--resume` - Resume if session already exists on this branch

**Examples:**
```bash
# Start new feature
python scripts/session.py start feature/user-auth --objective "Implement JWT authentication"

# Start with resume fallback
python scripts/session.py start feature/payments --resume
```

**Behavior:**
1. Creates/checks out git branch
2. Initializes session directory (`.git/sessions/<branch>/`)
3. Loads project context from `.session/`
4. Generates agent brief
5. Displays user brief with status

---

### `resume` - Resume Existing Session

```bash
python scripts/session.py resume [branch-name]
```

**Arguments:**
- `branch-name` (optional) - Specific branch to resume; defaults to current

**Examples:**
```bash
# Resume current branch
python scripts/session.py resume

# Resume specific branch
python scripts/session.py resume feature/oauth-integration
```

**Behavior:**
1. Checks out specified branch (if provided)
2. Loads session context
3. Analyzes git history since last session
4. Generates comprehensive brief
5. Displays current status

---

### `checkpoint` - Create Checkpoint

```bash
python scripts/session.py checkpoint [options]
```

**Options:**
- `--label "text"` - Checkpoint label for easy reference
- `--message "text"` - Git commit message
- `--decision "text"` - Record architectural decision

**Examples:**
```bash
# Simple checkpoint
python scripts/session.py checkpoint --label "oauth-complete"

# With decision
python scripts/session.py checkpoint \
  --label "auth-interface" \
  --decision "Using interface segregation for auth providers"

# With custom message
python scripts/session.py checkpoint \
  --label "tests-passing" \
  --message "feat(auth): Add comprehensive test suite"
```

**Behavior:**
1. Captures current git state
2. Analyzes code changes
3. Updates progress toward objectives
4. Creates enhanced git commit with metadata
5. Saves checkpoint metadata

---

### `end` - End Session

```bash
python scripts/session.py end [options]
```

**Options:**
- `--handoff` - Generate handoff document (default: true)
- `--merge-to <branch>` - Merge to target branch after ending
- `--summary` - Generate session summary (default: true)

**Examples:**
```bash
# End with handoff
python scripts/session.py end

# End and merge
python scripts/session.py end --merge-to main

# End without handoff
python scripts/session.py end --no-handoff
```

**Behavior:**
1. Final comprehensive state capture
2. Calculates session metrics
3. Generates handoff document
4. Archives session data
5. Optional: merges to target branch
6. Displays accomplishments summary

---

### `switch` - Switch Sessions

```bash
python scripts/session.py switch <branch-name>
```

**Arguments:**
- `branch-name` - Target session/branch to switch to

**Examples:**
```bash
# Switch to hotfix
python scripts/session.py switch hotfix/critical-bug

# Back to feature
python scripts/session.py switch feature/main-work
```

**Behavior:**
1. Saves current session state
2. Checks out target branch
3. Loads target session context
4. Displays quick brief
5. Highlights differences

---

## Context Query Commands

### `status` - Session Status

```bash
python scripts/session.py status [options]
```

**Options:**
- `--verbose` - Include detailed information
- `--objectives` - Show only objectives
- `--blockers` - Show only blockers

**Examples:**
```bash
# Quick status
python scripts/session.py status

# Detailed status
python scripts/session.py status --verbose

# Just objectives
python scripts/session.py status --objectives
```

**Output includes:**
- Current objectives and progress
- Active blockers
- Recent changes summary
- Time in session
- Quality metrics (if available)
- Next recommended actions

---

### `history` - Session History

```bash
python scripts/session.py history [options]
```

**Options:**
- `--count N` - Number of sessions to show (default: 10)
- `--metrics` - Include velocity and quality metrics
- `--since <date>` - Filter by date (YYYY-MM-DD format)

**Examples:**
```bash
# Last 10 sessions
python scripts/session.py history

# Last 5 with metrics
python scripts/session.py history --count 5 --metrics

# Since specific date
python scripts/session.py history --since 2025-10-01
```

**Output includes:**
- Session timeline
- Objectives completed per session
- Velocity trends (if --metrics)
- Quality progression (if --metrics)

---

## Management Commands

### `objectives` - Manage Objectives

```bash
python scripts/session.py objectives <action> [options]
```

**Actions:**
- `add "text"` - Add new objective
- `complete <id>` - Mark objective complete
- `list` - Show all objectives

**Examples:**
```bash
# Add objective
python scripts/session.py objectives add "Implement webhook handlers"

# Complete objective
python scripts/session.py objectives complete obj-1

# List objectives
python scripts/session.py objectives list
```

---

### `blockers` - Manage Blockers

```bash
python scripts/session.py blockers <action> [options]
```

**Actions:**
- `add "text"` - Add new blocker
- `resolve <id>` - Mark blocker resolved
- `list` - Show all blockers

**Examples:**
```bash
# Add blocker
python scripts/session.py blockers add "Waiting on API keys"

# Resolve blocker
python scripts/session.py blockers resolve blk-1

# List blockers
python scripts/session.py blockers list
```

---

### `decisions` - Log Decisions

```bash
python scripts/session.py decisions <action> [options]
```

**Actions:**
- `add "text"` - Record architectural decision
- `list` - Show decision log

**Options (for add):**
- `--rationale "text"` - Decision rationale
- `--alternatives "text"` - Alternatives considered

**Examples:**
```bash
# Record decision
python scripts/session.py decisions add "Using JWT over sessions" \
  --rationale "Stateless auth for microservices"

# With alternatives
python scripts/session.py decisions add "Repository pattern for data access" \
  --rationale "Separates domain from persistence" \
  --alternatives "Active Record: Too coupled to database"

# List decisions
python scripts/session.py decisions list
```

---

## Analysis Commands

### `analyze` - Session Analysis

```bash
python scripts/session.py analyze [options]
```

**Options:**
- `--velocity` - Calculate velocity metrics
- `--patterns` - Detect coding patterns
- `--recommendations` - Generate recommendations

**Examples:**
```bash
# Basic analysis
python scripts/session.py analyze

# With velocity
python scripts/session.py analyze --velocity

# Full analysis
python scripts/session.py analyze --velocity --patterns --recommendations
```

**Output includes:**
- Session health score
- Pattern compliance
- Code quality trends
- Velocity calculations (if --velocity)
- Recommended actions (if --recommendations)

---

### `compare` - Compare Sessions

```bash
python scripts/session.py compare <session-id> [options]
```

**Options:**
- `--changes` - Show code changes
- `--metrics` - Compare metrics

**Examples:**
```bash
# Compare with previous session
python scripts/session.py compare session-2025-10-30

# With detailed changes
python scripts/session.py compare session-2025-10-30 --changes
```

---

### `report` - Generate Reports

```bash
python scripts/session.py report [options]
```

**Options:**
- `--weekly` - Weekly summary
- `--project` - Complete project summary
- `--format <type>` - Output format (markdown, json, html)

**Examples:**
```bash
# Weekly report
python scripts/session.py report --weekly

# Project summary
python scripts/session.py report --project --format markdown
```

---

## Common Workflows

### Starting Your Day

```bash
# Resume where you left off
python scripts/session.py resume

# Check what needs to be done
python scripts/session.py status
```

### During Development

```bash
# Checkpoint at milestones
python scripts/session.py checkpoint --label "api-implemented"

# Record important decisions
python scripts/session.py decisions add "Using Redis for caching" \
  --rationale "Fast, simple, proven for this use case"

# Track blockers
python scripts/session.py blockers add "Need database credentials"
```

### Ending Your Day

```bash
# End with comprehensive handoff
python scripts/session.py end

# Or end and merge
python scripts/session.py end --merge-to main
```

### Context Switching

```bash
# Urgent issue
python scripts/session.py switch hotfix/prod-issue

# Back to feature work
python scripts/session.py switch feature/current-work
```

---

## Exit Codes

All commands return standard exit codes:
- `0` - Success
- `1` - Error (check output for details)

---

## Environment Variables

Session management respects these environment variables:

- `SESSION_CONFIG` - Path to custom config file
- `SESSION_VERBOSE` - Enable verbose output (true/false)
- `GIT_DIR` - Custom git directory location

---

## Integration with Git

Session management integrates with git through:

**Git Hooks:**
- `post-checkout` - Auto-load session on branch switch
- `prepare-commit-msg` - Inject session metadata
- `post-commit` - Update progress tracking

**Git Configuration:**
- Uses `user.name` and `user.email` for session attribution
- Respects `.gitignore` for file tracking
- Works with all git workflows (merge, rebase, etc.)

---

## Tips & Tricks

**Aliases:**
Add to your shell profile for quick access:
```bash
alias ss='python scripts/session.py status'
alias sc='python scripts/session.py checkpoint'
alias se='python scripts/session.py end'
```

**Quick Checkpoints:**
```bash
# Label-only checkpoint (uses current time as message)
python scripts/session.py checkpoint --label "milestone"
```

**Verbose Troubleshooting:**
```bash
# Any command can use --verbose for detailed output
python scripts/session.py status --verbose
```
