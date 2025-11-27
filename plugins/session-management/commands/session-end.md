---
description: End session with comprehensive handoff generation
---

# Session End Workflow

Execute the session-management skill's finish workflow to create a comprehensive handoff.

## Step 1: Create Final Checkpoint

First, automatically create a final checkpoint to capture the current state:

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/session-management/scripts
python session.py checkpoint --label "session-end"
```

This captures all uncommitted work and current metrics.

## Step 2: Gather Handoff Information

Use `AskUserQuestion` to collect information for the handoff document:

### Question 1: What Did You Accomplish?

Ask: "What did you accomplish in this session?"

Options:
- Analyze the session checkpoints and git commits to suggest:
  - **"Completed [feature/task from objectives]"**
  - **"Fixed [issues addressed]"**
  - **"Implemented [components created]"**
  - **"Refactored [areas improved]"**
- **Other** - Let user type custom accomplishments

### Question 2: What Decisions Were Made?

Ask: "Were there any important decisions or trade-offs made during this session?"

Options:
- **"Chose [technology/approach] because [reason]"** - Technical decision
- **"Decided to defer [feature] due to [constraint]"** - Scope decision
- **"No major decisions"** - Skip this section
- **Other** - Let user type custom decisions

### Question 3: What Should Next Session Remember?

Ask: "What context or next steps should be documented for the next session?"

Options:
- **"Continue with [specific task]"** - Next task note
- **"Watch out for [potential issue]"** - Warning note
- **"Remember to [action item]"** - Action reminder
- **"Review [code/docs] before proceeding"** - Review reminder
- **Other** - Let user type custom notes

### Question 4: Git Push Options

Ask: "Should we push commits to the remote repository?"

Options:
- **Yes, push to remote** - Push all commits (proceed with confirmation)
- **No, keep local** - Don't push (useful for WIP)
- **Ask for confirmation first** - Show what will be pushed, then confirm

## Step 3: Generate Handoff Document

Based on collected inputs, execute the session end command:

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/session-management/scripts

# Generate handoff and push
python session.py end --push

# Generate handoff without push
python session.py end --no-push

# With merge to main
python session.py end --merge-to main --push
```

The script will:
- Generate comprehensive handoff document with:
  - Session summary (start time, duration, objectives)
  - Accomplishments (from collected inputs)
  - Decisions made (from collected inputs)
  - Context for next session (from collected inputs)
  - Metrics (commits, files changed, tests added)
  - Git status (branch, uncommitted changes)
- Save to `.sessions/handoffs/handoff_[timestamp].md`
- Optionally push commits to remote
- Update session state to "ended"

## Step 4: Confirm and Finalize

Report to user:
- Handoff document location
- Session summary (time spent, accomplishments)
- Git status (commits pushed, branch state)
- Next session recommendations

Optionally ask:

Ask: "Would you like to merge this branch?"

Options:
- **Merge to main** - Merge current branch to main
- **Merge to develop** - Merge to develop branch
- **Create pull request** - Guide PR creation
- **Keep branch** - Don't merge, keep for next session

---

## Use This Command

When ending a work session:
- End of day or before extended break
- After completing feature or fix
- Before context switching to different project
- When wrapping up and need handoff for future you or teammates

## Integration Notes

- Integrates with **tdd-workflow** for test metrics in handoff
- Uses checkpoint system for comprehensive state capture
- Handoffs saved to `.sessions/handoffs/` directory
- Session state preserved in `.sessions/state.json`
