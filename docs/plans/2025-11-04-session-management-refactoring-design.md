# Session Management Refactoring Design

**Date**: 2025-11-04
**Status**: Design Complete
**Goal**: Transform session management into a git-native onboarding system that minimizes context-switching time for developers working across multiple projects

## Problem Statement

Developers working on multiple projects face significant friction when context-switching:
- Days may pass between sessions on a specific project
- No systematic way to quickly recall: where I left off, what's broken, what's next
- Both human developers and AI agents need rapid re-immersion
- Current session skill exists but doesn't effectively support this workflow

## Design Philosophy

Session management is a **git-native onboarding system** that:
- **Bridges sessions** by capturing and restoring full project context
- **Observes and orchestrates** (not duplicates) superpowers workflows
- **Focuses on rapid re-immersion** - get to Designing, Developing, or Debugging fast
- **Project-focused** - no cross-project tracking, deep single-project intelligence
- **Balances speed with richness** - checkpoints are quick, session end is comprehensive

## Architecture Overview

### Two-Skill System

**Skill 1: `project-status-report`** (NEW - standalone skill)
- Generates comprehensive project health and status reports
- Invokable independently: `/project-report`
- Consumed by session-management but also useful mid-session
- Sections: Health → Git → Recent Session → Open Work → Backlog → AI Suggestions

**Skill 2: `session-management`** (REFACTORED)
- Manages session lifecycle: start → work → checkpoint → pause → finish
- Slash commands: `/session-start`, `/checkpoint`, `/session-end`
- Uses project-status-report for onboarding
- Observes superpowers workflows, orchestrates git operations

### Why Two Skills?

**Separation of concerns**:
- Developer can check `/project-report` anytime without session overhead
- Other future skills can consume project status (planning, debugging, etc.)
- Session-management focuses purely on lifecycle, not reporting logic
- Reusable primitive vs. specialized workflow

## Storage Structure

### Project-Local Only (`.sessions/`)

```
.sessions/
├── log                              # Session timeline (append-only)
├── checkpoints/
│   ├── 2025-11-04T14-30-00.md      # Auto-named by datetime
│   ├── 2025-11-04T16-45-00.md      # Automatic snapshots
│   └── 2025-11-04T18-00-00-HANDOFF.md  # Session end handoff
└── state.json                       # Current session state
```

**Design Principle**: Everything stays in the project. No global session registry. The skill doesn't need to be cross-project.

## Core Workflows

### 1. Session Start (`/session-start`)

**Purpose**: Rapid re-immersion for both human and AI

**Flow**:

1. **Generate project status report**
   - Invoke `project-status-report` skill
   - Get comprehensive health, git status, recent work, open items

2. **Present context-aware options** (AI-driven)
   - **If health issues detected**: "⚠️ Fix 3 failing tests before new work?"
   - **If unfinished session exists**: "Resume feature/auth (2 open objectives)?"
   - **If clean slate**: "Start new work" (shows backlog items)
   - **Smart adaptation** based on project state

3. **Ask multiple-choice question**: "What do you want to work on?"
   - Options generated from report analysis
   - AI reasoning included with each option

4. **Branch decision** (context-aware best practices)
   - **Resuming work**: Checkout existing branch
   - **New work**: "Use existing branch or create new?" (shows active branches with context)
   - **Health fix**: Suggest current branch or hotfix branch based on severity
   - **AI provides best practice guidance** based on git state

5. **Load context**
   - Read `.sessions/checkpoints/{latest for this branch}.md`
   - Load from `.ccmp/state.json` (TDD mode, context health, etc.)
   - Auto-load relevant `claude.md` files (via claude-context-manager integration)

6. **Create session log entry**
   - Append to `.sessions/log`
   - Record: timestamp, branch, objectives, initial project state

7. **Brief both human and AI**
   - **Human**: "✅ Session ready on feature/auth - 2 objectives, context loaded"
   - **AI**: Receives full context (architecture, decisions, blockers, recent changes, patterns)

**Output**: Developer and AI are both fully contextualized and ready to work

### 2. Checkpoint (`/checkpoint`)

**Purpose**: Quick save points during work - fast but comprehensive

**Flow**:

1. **Automatic capture** (fully inferred):
   - Git diff analysis (files changed, additions/deletions)
   - Recent commits since last checkpoint
   - Metrics: test count, coverage delta, time elapsed
   - TDD cycle detection (observe tdd-workflow state)
   - Context health check (via claude-context-manager)

2. **Infer what changed**:
   - Parse git diff for modified modules/functions
   - Detect new files, deleted files
   - Check for new TODOs, FIXMEs in changed files
   - Analyze commit messages for decisions

3. **Optional prompt**: "Add checkpoint notes? (optional, press Enter to skip)"
   - If provided: added to checkpoint document
   - If skipped: checkpoint still comprehensive from automatic analysis
   - **Quick by default** - no required input

4. **Generate checkpoint document**: `.sessions/checkpoints/{datetime}.md`

```markdown
# Checkpoint: 2025-11-04T14-30-00

## What Changed
- Modified: src/auth/oauth.py (+45, -12)
- Added: tests/test_oauth.py (+120)
- Test coverage: 79% → 84%

## Commits Since Last Checkpoint
- abc1234 feat(auth): add OAuth provider interface

## Why It Changed
- Implemented PKCE flow for OAuth security
- [from commit messages and code analysis]

## TDD Cycles
- Completed: 2 cycles this session
- Current phase: GREEN

## Context Health
- ✅ All context files up to date

## What's Next
- GitHub OAuth provider (inferred from TODOs)
- Token refresh logic pending

## Notes
[optional user notes here]
```

5. **Git commit handling**:
   - **If uncommitted changes exist**: "Stage and commit changes? [Y/n]"
   - **If yes**: Use superpowers git workflow to create commit
   - **If no**: Checkpoint saved, git unchanged
   - **Never forces commits** - developer controls git

6. **Update session state**: `.sessions/state.json` updated with latest checkpoint time

**Key Principle**: Checkpoints are **quick** (no required prompts), but **rich** (automatic analysis). Session notes are for session end.

### 3. Pause Session

**Purpose**: Explicit pause point (same as checkpoint + log entry)

**Flow**:
- Runs checkpoint workflow (automatic capture + optional notes)
- Adds session log entry: "Session paused at {datetime}"
- Updates `.sessions/state.json`: `"status": "paused"`
- **No git push** (just local save for resuming later)

**Use case**: Switching to different project, end of day, interruption

### 4. Finish Session (`/session-end`)

**Purpose**: Comprehensive knowledge capture and handoff generation

**Flow**:

1. **Run checkpoint workflow first** (capture final state)

2. **Git operations** (Smart handling with safety):
   - Check working tree status
   - **If uncommitted changes**:
     - "You have uncommitted changes. Create WIP commit? [Y/n]"
     - If yes: Create commit with session metadata
   - **If clean**: Proceed to push
   - **Push to remote**: "Push {N} commits to origin/{branch}? [Y/n]"
     - Show list of commits to be pushed
     - Confirm before pushing
   - **Always ask for confirmation** - never force push

3. **Session notes prompt** (this is the knowledge capture moment):

```
Session Summary Notes:

What did you accomplish?
> Implemented Google OAuth with PKCE flow, added 12 tests

Key decisions made?
> Chose PKCE over standard flow for better security against code interception

What to remember for next session?
> Ready to implement GitHub OAuth using same pattern. Token refresh is next priority.
```

4. **Generate handoff document**: `.sessions/checkpoints/{datetime}-HANDOFF.md`

```markdown
# Session Handoff: 2025-11-04

**Branch**: feature/auth
**Duration**: 3h 15m
**Commits**: 5 pushed to origin

## Session Summary

Implemented Google OAuth with PKCE flow, added 12 tests. Chose PKCE over standard
flow for better security against code interception. Ready to implement GitHub OAuth
using same pattern. Token refresh is next priority.

## What Changed (This Session)

**Checkpoints**: 3 created
**Commits**: 5 pushed
**Files modified**: 8
**Tests added**: 15
**Coverage**: 79% → 84%

### Files Changed
- src/auth/oauth.py (+145, -23)
- src/auth/providers/google.py (new, +89)
- tests/test_oauth.py (+120)
- tests/test_google_oauth.py (new, +95)

## Why It Changed (Decisions Made)

**PKCE Flow for OAuth**
- Rationale: Protection against code interception attacks
- Alternative considered: Standard OAuth flow (less secure for mobile/SPA)
- Reference: checkpoint 2025-11-04T14-30-00

## What's Next (Open Work)

**Objectives Remaining**:
- [ ] GitHub OAuth provider (next up - use Google pattern)
- [ ] Token refresh logic
- [ ] Rate limiting for OAuth endpoints

**TODOs in Code**:
- src/auth/oauth.py:45 - TODO: Add rate limiting
- src/auth/oauth.py:78 - FIXME: Handle token expiry edge case

## Mental Context

The Google OAuth implementation went smoothly. PKCE flow adds complexity but
worth it for security. GitHub OAuth should be straightforward using the same
provider pattern. Watch out for GitHub's different token scopes.

## Blockers

None currently.

## Context Health

✅ All context files current
✅ Tests passing
⚠️ Coverage at 84% (target 90% - consider adding edge case tests)

## TDD Metrics (Session)

- Cycles completed: 4
- Discipline score: 100/100
- Average cycle time: 25 minutes

## Next Steps (AI Suggested)

1. **Implement GitHub OAuth provider** (~2 hours)
   - High: Copy Google pattern, straightforward
   - Builds momentum on current work

2. **Add token refresh logic** (~1 hour)
   - Medium: Addresses technical debt and TODO
   - Stay in auth domain while context fresh

3. **Write integration tests** (~1 hour)
   - Medium: Increase coverage toward 90% goal
   - Test edge cases before moving on
```

5. **Update session log**: Add end entry with summary metadata

6. **Update state**: `.sessions/state.json` → `"status": "completed"`

7. **Brief**:
   ```
   ✅ Session ended. 5 commits pushed to origin/feature/auth.
   📄 Handoff generated: .sessions/checkpoints/2025-11-04T18-00-00-HANDOFF.md
   ```

**Key Principle**: Session end is **knowledge capture** moment. Rich notes, comprehensive handoff, full context for next session.

## Project Status Report Design

### Purpose

Standalone skill providing comprehensive project health and status analysis.

### Invocation

- **Standalone**: `/project-report` (check status anytime)
- **Internal**: Called by session-management during `/session-start`

### Report Sections (Priority Order)

Report sections follow priority: **E, A, B, C, D, F**

#### Section E: Health Indicators (PRIORITY 1 - What's Broken)

```markdown
## 🏥 Health Indicators

✅ Tests: 156 passing
❌ Linting: 3 errors in src/auth/oauth.py
⚠️  Coverage: 84% (target: 90%)
✅ Build: Success (last run: 2 hours ago)
⚠️  Context: 2 files stale (>30 days since update)

**Critical Issues**: 1
- Linting errors blocking CI

**Warnings**: 2
- Coverage below target
- Stale context files may need refresh
```

**Data sources**:
- Test runner output (pytest, jest, etc.)
- Linter output (pylint, eslint, etc.)
- Coverage reports
- Build logs
- `.ccmp/state.json` (context health from claude-context-manager)

#### Section A: Git Status (PRIORITY 2 - Where Am I)

```markdown
## 📍 Git Status

**Current Branch**: feature/auth
**Status**: Ahead of origin/feature/auth by 2 commits
**Uncommitted**: 3 files modified
**Untracked**: 1 file

**Active Branches** (recent):
- feature/auth (current, last commit 2 hours ago)
- hotfix/timeout-bug (last commit 3 days ago)
- feature/user-profiles (last commit 1 week ago)

**Remote Sync**:
- origin/main: 15 commits ahead (needs rebase)
```

**Data sources**:
- `git status`, `git branch -v`, `git log`
- Branch activity analysis

#### Section B: Recent Session Summary (PRIORITY 3 - Where I Left Off)

```markdown
## 📖 Recent Session Summary

**Last Session**: 2025-11-03 (yesterday)
**Branch**: feature/auth
**Duration**: 2h 45m
**Last Checkpoint**: 2025-11-03T16-30-00

**Accomplished**:
- Implemented Google OAuth provider
- Added PKCE flow support
- 12 unit tests added

**Left Off**:
- Ready to implement GitHub OAuth provider
- Token refresh logic pending

**Mental Context**:
"Google OAuth went smoothly, GitHub should be straightforward using same pattern"
```

**Data sources**:
- `.sessions/log` (last session entry)
- `.sessions/checkpoints/{latest}.md`
- Last checkpoint notes

#### Section C: Open Work Items (PRIORITY 4 - What Needs Doing)

```markdown
## 📋 Open Work Items

**Objectives** (feature/auth):
- [x] OAuth provider interface
- [x] Google OAuth (completed last session)
- [ ] GitHub OAuth (next)
- [ ] Token refresh

**Active Blockers**: None

**TODOs in Code**:
- src/auth/oauth.py:45 - TODO: Add rate limiting
- src/auth/oauth.py:78 - FIXME: Handle token expiry edge case
- src/auth/providers/google.py:23 - TODO: Add refresh token handling

**FIXMEs**: 1
**TODOs**: 2
```

**Data sources**:
- `.sessions/state.json` (objectives)
- Code scan for TODO/FIXME markers
- `.sessions/checkpoints/{latest}.md` (blockers)

#### Section D: Backlog Snapshot (PRIORITY 5 - What's Planned)

```markdown
## 📚 Backlog Snapshot

**From Issue Tracker**:
- #42: Add user profile management (8 story points)
- #55: Implement 2FA (5 story points)
- #61: OAuth token refresh (3 story points)

**Technical Debt**:
- Refactor auth middleware (flagged 2 weeks ago)
- Update legacy API endpoints (flagged 1 month ago)
```

**Data sources**:
- Issue tracker integration (GitHub Issues, Jira, etc.) - optional
- Manual backlog in `.sessions/backlog.md` - optional
- Code comments marked as technical debt

#### Section F: Suggested Next Actions (PRIORITY 6 - AI Guidance)

```markdown
## 💡 Suggested Next Actions

**AI Analysis**: Based on current state, here are recommended next steps:

### 1. ⚠️ Address Linting Errors FIRST (BLOCKING)
**Why**: 3 errors in src/auth/oauth.py blocking CI
**Effort**: ~10 minutes
**Impact**: Unblocks deployment pipeline
**Priority**: CRITICAL

### 2. Resume feature/auth Work (HIGH MOMENTUM)
**Why**: High context, clear next steps, 2 objectives remaining
**Next**: Implement GitHub OAuth using Google pattern
**Effort**: ~2 hours
**Impact**: Completes major feature milestone
**Priority**: HIGH

### 3. Alternative: Fix Token Refresh (RELATED WORK)
**Why**: Addresses TODO and backlog item #61, stay in auth domain
**Effort**: ~1 hour
**Impact**: Reduces technical debt, completes small feature
**Priority**: MEDIUM
```

**Generation logic**:
- **If critical health issues**: Prioritize fixes
- **If momentum on branch**: Suggest continuation
- **If clean slate**: Suggest backlog items
- **Always provide reasoning** for suggestions
- **Estimate effort** based on code analysis
- **Consider context freshness** (prefer related work)

### Report Template

Full report combines all sections in priority order, with AI-generated suggestions contextual to the current state.

### Implementation

**Python script** (`scripts/report.py`):
- Modular analyzers for each section
- Health check module
- Git analysis module
- Work items scanner
- AI suggestion generator
- Template rendering

**Output formats**:
- Markdown (default, for display)
- JSON (for programmatic consumption)

## Integration with Superpowers

### Design Principle

Session management **observes and orchestrates** superpowers workflows, never duplicates them.

### Observer Pattern (Session Watches Superpowers)

**What session observes**:
- **TDD cycles**: Read `.ccmp/state.json` for tdd-workflow cycle count
- **Debugging sessions**: Observe systematic-debugging invocations (future)
- **Verification runs**: Note when verification-before-completion runs
- **Test outcomes**: Track test results over time

**How it observes**:
- Read `.ccmp/state.json` (shared plugin state)
- Parse commit messages for superpowers markers
- Track file changes and correlate with workflow states

**What it captures**:
```markdown
## Session Metrics

**TDD Workflow**:
- Cycles completed: 4
- Discipline score: 100/100
- Average cycle time: 25 minutes

**Verification**:
- Ran 3 times this session
- All checks passed

**Debugging**:
- systematic-debugging used: 1 time
- Issue resolved: timeout in auth flow
```

### Orchestrator Pattern (Session Invokes Superpowers)

**Git operations**:
- Session **never implements git commands directly**
- Use superpowers git workflow for:
  - Commits (with proper formatting)
  - Pushes (with safety checks)
  - Branch operations (with best practices)

**Example orchestration**:
```python
# In checkpoint workflow
if user_wants_to_commit:
    # Don't run: subprocess.run(["git", "commit", ...])
    # Instead: Invoke superpowers git workflow
    invoke_superpowers_skill("git-commit", metadata=checkpoint_data)
```

**Verification** (optional):
- At session end, optionally trigger `verification-before-completion`
- Ensures clean state before handoff

### Context Provider (Session Feeds Superpowers)

**Shared state** (`.ccmp/state.json`, `.sessions/state.json`):
- Session objectives visible to all skills
- Recent decisions available for debugging context
- Blockers visible to planning skills

**Example context sharing**:
```json
{
  "session-management": {
    "active": true,
    "branch": "feature/auth",
    "objectives": [
      "Implement OAuth providers",
      "Add token refresh"
    ],
    "mode": "tdd"
  }
}
```

**How superpowers use session context**:
- `systematic-debugging` can reference session objectives
- `test-driven-development` knows session is in TDD mode
- Future skills can query session state for decision-making

### Integration Flow Example

```
Developer: /session-start

1. project-status-report generates health report
   └─> Reads .ccmp/state.json for context health
   └─> Runs git commands for status
   └─> AI generates suggestions

2. Session presents options: "Resume feature/auth (2 objectives)?"

3. Developer picks option

4. Session loads context, sets up branch
   └─> Updates .sessions/state.json
   └─> Updates .ccmp/state.json (session active)

5. Developer works using superpowers TDD workflow
   └─> tdd-workflow updates .ccmp/state.json (cycle count)
   └─> Session observes, doesn't interfere

6. Developer: /checkpoint
   └─> Session captures state
   └─> Reads .ccmp/state.json for TDD metrics
   └─> Optionally: Invokes superpowers git-commit

7. Developer: /session-end
   └─> Session creates final checkpoint
   └─> Invokes superpowers git-push (with confirmation)
   └─> Generates comprehensive handoff
   └─> Updates .ccmp/state.json (session inactive)
```

**Key Principle**: Session management is a **coordination layer** that makes superpowers workflows session-aware, without duplicating their functionality.

## Implementation Plan

### Phase 1: Project Status Report Skill

**New plugin**: `plugins/project-status-report/`

**Components**:
1. Health check analyzer
2. Git status analyzer
3. Work items scanner
4. AI suggestion generator
5. Report template renderer
6. CLI: `scripts/report.py`
7. Slash command: `/project-report`

**Deliverable**: Standalone skill that generates comprehensive project reports

### Phase 2: Session Management Refactor

**Refactor plugin**: `plugins/session-management/`

**Changes**:
1. Refactor `scripts/session.py`:
   - Integrate project-status-report for session start
   - Implement automatic checkpoint capture
   - Add smart git handling (Option C)
   - Implement session notes prompts for finish

2. Add checkpoint logic (`scripts/checkpoint.py`):
   - Automatic inference from git diff
   - TDD cycle observation
   - Context health integration

3. Add handoff generation (`scripts/handoff.py`):
   - Comprehensive template
   - Session summary compilation
   - AI-generated next steps

4. Add slash commands:
   - `/session-start`
   - `/checkpoint`
   - `/session-end`

5. Update SKILL.md with new workflows

**Deliverable**: Refactored session management with rapid onboarding

### Phase 3: Integration & Testing

**Integration work**:
1. Ensure `.ccmp/state.json` coordination works
2. Test with tdd-workflow observation
3. Test with claude-context-manager health checks
4. Verify superpowers git workflow invocation

**Testing**:
1. Test session start with various project states
2. Test checkpoint workflow (automatic capture)
3. Test finish workflow (git operations, handoff)
4. Test cross-session resume (handoff → start)

**Documentation**:
1. Update skill SKILL.md files
2. Add examples and guides
3. Document integration patterns

## File Structure (Final)

```
plugins/
├── project-status-report/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── skills/project-status-report/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── report.py (main CLI)
│   │   │   ├── health_check.py
│   │   │   ├── git_analysis.py
│   │   │   ├── work_items.py
│   │   │   └── ai_suggestions.py
│   │   └── templates/
│   │       └── report.md
│   └── commands/
│       └── project-report.md
│
└── session-management/
    ├── .claude-plugin/
    │   └── plugin.json
    ├── skills/session-management/
    │   ├── SKILL.md (refactored)
    │   ├── scripts/
    │   │   ├── session.py (refactored)
    │   │   ├── checkpoint.py (new)
    │   │   ├── handoff.py (new)
    │   │   └── init_session.py (unchanged)
    │   └── templates/
    │       ├── checkpoint.md
    │       └── handoff.md
    └── commands/
        ├── session-start.md
        ├── checkpoint.md
        └── session-end.md

# In each project using session management:
.sessions/
├── log
├── checkpoints/
│   ├── {datetime}.md
│   └── {datetime}-HANDOFF.md
└── state.json
```

## Success Criteria

**For developers**:
- [ ] Can start session and be fully contextualized in < 2 minutes
- [ ] Session start report immediately shows what's broken, where left off, what's next
- [ ] Checkpoints are fast (no required input) but comprehensive (rich automatic capture)
- [ ] Session end generates handoff that makes next session seamless
- [ ] Git best practices automated (with safety confirmations)

**For AI agents**:
- [ ] Receive full project context on session start (architecture, decisions, patterns)
- [ ] Can access current objectives and blockers throughout session
- [ ] Session notes and decisions preserved for future reference

**For integration**:
- [ ] Observes superpowers workflows (TDD cycles, verification runs)
- [ ] Invokes superpowers git workflows (no duplicate implementation)
- [ ] Coordinates via .ccmp/state.json without conflicts
- [ ] Works standalone even if other CCMP plugins not installed

## Future Enhancements (Out of Scope)

**Not included in this design** (potential future work):
- Cross-project session tracking (global session registry)
- Team collaboration features (shared sessions, handoffs between developers)
- Issue tracker integration (automatic backlog sync)
- Metrics dashboards (session analytics, velocity tracking)
- AI-driven session recommendations (when to checkpoint, when to finish)

**Reason for exclusion**: Focus on core rapid re-immersion workflow first. These can be added incrementally based on usage patterns.

## Design Rationale Summary

### Key Decisions

**Why two skills?**
- Separation of concerns: reporting vs. lifecycle management
- Reusability: report useful outside session context
- Simplicity: each skill has single clear purpose

**Why automatic checkpoints?**
- Speed: no required prompts during work
- Richness: git diff analysis provides comprehensive capture
- Balance: optional notes available but not required

**Why comprehensive session end?**
- Knowledge capture: most valuable information is "what to remember"
- Handoff quality: next session depends on good handoff
- One-time cost: worth the investment for future sessions

**Why observer pattern for superpowers?**
- No duplication: use proven workflows
- Coordination: session makes workflows session-aware
- Flexibility: works even if superpowers not installed

**Why project-local storage?**
- Simplicity: no global state to manage
- Git-native: session history committed with code
- Focus: deep project intelligence, not cross-project tracking

### Alignment with Goals

**Minimizes context-switching time**:
- Session start report provides instant onboarding
- AI-guided options reduce decision paralysis
- Context automatically loaded (architecture, decisions, patterns)

**Seeds both human and AI**:
- Human gets visual report with actionable options
- AI receives structured context (objectives, decisions, blockers)
- Shared understanding from same source of truth

**Extends superpowers, doesn't duplicate**:
- Observer pattern for tracking workflows
- Orchestrator pattern for invoking git operations
- Context provider for feeding session state to skills

**Git best practices automated**:
- Smart commit handling (WIP detection)
- Push confirmation with preview
- Session metadata in commits
- Branch management with best practice guidance

## Next Steps

1. **Validate design** with stakeholder ✅ (completed via brainstorming)
2. **Write implementation plan** with detailed tasks
3. **Build project-status-report skill** (Phase 1)
4. **Refactor session-management skill** (Phase 2)
5. **Integration testing** (Phase 3)
6. **Documentation** and examples

---

**Design Status**: ✅ Complete and Validated
**Ready for**: Implementation planning and execution
