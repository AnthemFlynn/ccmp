---
description: Start or resume coding session with AI-guided context loading
---

# Session Start Workflow

Execute the session-management skill's start workflow using this step-by-step process.

## Step 1: Generate Project Status Report

First, generate a comprehensive project status report to understand current state:

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/project-status-report/scripts/report.py
```

Or invoke the project-status-report skill if available.

The report will show:
- Health indicators (tests, linting, coverage)
- Git status (current branch, uncommitted changes, active branches)
- Recent session summary
- Open work items (TODOs, FIXMEs, objectives)

## Step 2: Gather User Inputs via AskUserQuestion

Use the `AskUserQuestion` tool to collect session configuration. Ask the following questions:

### Question 1: What to Work On

Ask: "What would you like to work on in this session?"

Options:
- **Resume existing work** - Continue from where you left off
- **Start new work** - Begin a new feature or task
- **Address health issues** - Fix test failures or other critical issues from the report

### Question 2: Branch Selection

Ask: "Which branch would you like to work on?"

Options should include:
- All active branches from the git status (show current branch indicator and last commit date)
- **Create new branch** option

**If user selects "Create new branch"**, proceed to Question 2a and 2b.

#### Question 2a: Branch Type (if creating new)

Ask: "What type of branch would you like to create?"

Options:
- **Hotfix branch** (hotfix/...) - For urgent bug fixes
- **Feature branch** (feature/...) - For new features
- **Bugfix branch** (fix/...) - For non-urgent bug fixes
- **Other** - Custom branch prefix

#### Question 2b: Branch Name (if creating new)

Ask: "What should we name the branch?"

Options:
- Suggest intelligent defaults based on:
  - Branch type selected
  - Health issues from report (e.g., "fix/test-failures")
  - TODOs from report (e.g., "feature/oauth-integration")
  - User's stated objective
- **Other** - Let user type custom name

### Question 3: Session Objectives

Ask: "What are your objectives for this session?"

Options:
- Suggest objectives based on context:
  - "Fix [specific health issue]"
  - "Implement [TODO item]"
  - "Complete [work from last session]"
- **Other** - Let user type custom objectives

## Step 3: Execute Session Start

Based on the collected inputs, execute the session.py script:

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/session-management/scripts
python session.py start [branch-name] --objective "[objectives]"
```

**Additional flags:**
- Add `--tdd` if objectives involve implementing features or fixing bugs
- Add `--resume` if user selected "Resume existing work"

The script will:
- Checkout or create the specified branch
- Initialize session state in `.sessions/state.json`
- Update plugin coordination state in `.ccmp/state.json`
- Load relevant context files (claude.md, architecture docs)

## Step 4: Load Session Context

After session initialization:

1. Check if `.sessions/state.json` was created successfully
2. Read any relevant claude.md files for the work area
3. Load previous session context if resuming
4. Present a summary to the user:
   - Current branch
   - Session objectives
   - Relevant context loaded
   - Next suggested actions

## Step 5: Ready to Work

Confirm to the user:
- Session is initialized
- Branch is ready
- Context is loaded
- Ready to begin work on stated objectives

---

## Use This Command When

- Starting work on a project after a break
- Returning after context switch between projects
- Beginning a new feature or bugfix
- Need to load full project context quickly

## Integration Notes

This command integrates with:
- **project-status-report** - For comprehensive health overview
- **claude-context-manager** - Auto-loads relevant claude.md files
- **tdd-workflow** - Enables TDD mode tracking if --tdd flag used
