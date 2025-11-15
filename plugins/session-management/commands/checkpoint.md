---
description: Create session checkpoint with automatic state capture
---

# Checkpoint Workflow

Execute the session-management skill's checkpoint workflow to save progress.

## Step 1: Analyze Current State

The checkpoint manager will automatically analyze:
- Git changes (modified, added, deleted files)
- TDD metrics (if TDD mode active)
- Session metrics (time elapsed, objectives completed)

## Step 2: Gather Optional Inputs (if desired)

Use `AskUserQuestion` to ask if the user wants to provide additional context:

Ask: "Would you like to add notes or create a git commit with this checkpoint?"

Options:
- **Just save checkpoint** - Create checkpoint document only
- **Add notes** - Prompt for checkpoint notes (proceed to Question 2a)
- **Add notes and commit** - Prompt for notes and create git commit (proceed to Question 2a and 2b)
- **Commit without notes** - Skip notes, create commit with auto-generated message (proceed to Question 2b)

### Question 2a: Checkpoint Notes (if requested)

Ask: "What notes would you like to add to this checkpoint?"

Options:
- **"Completed [feature/task]"** - Standard completion note
- **"Work in progress on [area]"** - WIP note
- **"Blocked on [issue]"** - Blocker note
- **Other** - Let user type custom notes

### Question 2b: Git Commit (if requested)

Ask: "Should we create a git commit for this checkpoint?"

Options:
- **Auto-generate commit message** - Use checkpoint analysis to create message
- **Custom commit message** - Let user type custom message
- **Skip commit** - Just save checkpoint, no git commit

## Step 3: Execute Checkpoint

Based on collected inputs, execute the checkpoint command:

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/session-management/scripts

# Basic checkpoint (no notes, no commit)
python session.py checkpoint

# With notes
python session.py checkpoint --notes "[user notes]"

# With notes and commit
python session.py checkpoint --notes "[user notes]" --commit

# With commit and custom message
python session.py checkpoint --commit --message "[custom message]"

# With TDD phase tracking
python session.py checkpoint --tdd-phase [RED|GREEN|REFACTOR]
```

The script will:
- Analyze git diff for changes
- Capture current metrics
- Generate checkpoint document
- Save to `.sessions/checkpoints/checkpoint_[timestamp].md`
- Optionally create git commit

## Step 4: Confirm Checkpoint Saved

Report to user:
- Checkpoint file location
- Summary of changes captured
- Git commit hash (if commit created)
- Current session progress

---

## Use This Command

At logical milestones during work:
- After completing a sub-task
- Before switching contexts
- When you want to save progress
- After each TDD cycle (RED, GREEN, REFACTOR)

## Integration Notes

- Integrates with **tdd-workflow** for automatic phase tracking
- Checkpoints saved to `.sessions/checkpoints/` directory
- Git commits tagged with checkpoint metadata
