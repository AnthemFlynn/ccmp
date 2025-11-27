# Git Commit Skill

Claude will help you write professional commit messages following industry standards (Conventional Commits).

## Installation

1. Install `git-commit.skill` in Claude
2. That's it

## Usage

### Smart Analysis (NEW!)

Stage your changes and ask Claude to help:

```
You: "Help me commit"

Claude: [runs analyze-diff.py to examine your code]

Based on your changes to auth/oauth.py:
- Added OAuth2 authentication functions
- Modified 15 lines in auth module

Suggested commit:
git commit -m"feat(auth): add OAuth2 authentication"
```

The analyzer examines:
- **File paths** → suggests scope (e.g., auth, api, ui)
- **Added code** → suggests type (feat, fix, refactor)
- **Function names** → generates description
- **Removed APIs** → detects breaking changes

You can also run it standalone:
```bash
git add .
python scripts/analyze-diff.py        # Get suggestion
python scripts/analyze-diff.py --commit  # Auto-commit with suggestion
```

### Manual Description

Or just describe what you changed:

```
You: "Help me write a commit - I added OAuth login"

Claude: git commit -m"feat(auth): add OAuth2 login support"
```

Claude will:
- Ask clarifying questions if needed
- Suggest the right commit type
- Format everything correctly
- Give you a ready-to-use git command

## Slash Commands

Use these commands for quick access to specific features:

- **`/commit`** - Smart commit helper (analyzes code if staged, otherwise interactive)
- **`/validate <message>`** - Check if a commit message is valid
- **`/types`** - Show all commit types with examples
- **`/scopes`** - Learn about scopes with project-specific suggestions
- **`/breaking`** - Guide for creating breaking change commits
- **`/changelog`** - Generate formatted changelog from commits
- **`/version`** - Calculate next semantic version number
- **`/examples`** - Show real-world commit examples
- **`/fix`** - Help amend or fix recent commits

## How /commit Works

**Smart and Adaptive:**

1. **Has staged changes?** → Analyzes your code automatically
2. **No staged changes?** → Asks what you changed, builds interactively
3. **You described it already?** → Uses your description

**Example with staged changes:**
```bash
git add auth/oauth.py
```
```
You: /commit

Claude: 📊 Analyzed your changes...
Suggested: git commit -m"feat(auth): add OAuth2 authentication"

Does this look good?
```

**Example without staged changes:**
```
You: /commit

Claude: No staged changes found. What did you change?

You: I added OAuth login

Claude: git commit -m"feat(auth): add OAuth login"
```

One command, smart behavior.

## Examples of What to Ask

- "Help me commit this change: [describe what you did]"
- "How should I write a commit for fixing the login bug?"
- "Is this commit message okay? fix: bug"
- "I made a breaking change to the API, help me write the commit"

## Commit Format

Claude follows this format:
```
type(scope): description

optional body

optional footer
```

**Types:** feat, fix, refactor, perf, style, test, docs, build, ops, chore

You don't need to memorize this - just describe what you did and Claude will format it correctly.

## Optional: Git Hook

If you want automatic validation, copy the included script:

```bash
cp scripts/validate.py .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

Now all commits are validated before they're created.

## That's It

No documentation to read. No commands to memorize. Just ask Claude for help.

---

**What it does:** Helps you write good commits  
**How to use it:** Ask Claude naturally  
**Learning curve:** Zero
