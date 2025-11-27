# Branching Strategy

## Overview

This repository follows a **trunk-based development** workflow with `dev` as the integration branch and `main` as the release branch.

## Branch Structure

```
main (releases only)
  ↑
  └── dev (integration)
       ↑
       ├── feature/my-feature
       ├── fix/bug-name
       └── refactor/component-name

hotfix/critical-issue → specific branch being fixed
```

## Branch Types

### `main` - Release Branch
- **Purpose**: Production-ready releases only
- **Protection**: Branch protection enabled
  - Requires pull request before merging
  - Requires linear history (no merge commits)
  - No force pushes allowed
  - No deletions allowed
- **Source**: Only accepts merges from `dev` branch
- **Naming**: Fixed name: `main`
- **Versioning**: Each merge to main should be tagged with semantic version (e.g., `v1.2.3`)

### `dev` - Integration Branch
- **Purpose**: Integration branch for all development work
- **Source**: Branched from `main` at project start
- **Merges**: Accepts feature, fix, and refactor branches
- **Updates**: Merges to `main` when ready for release
- **Naming**: Fixed name: `dev`

### Feature Branches
- **Purpose**: New features or enhancements
- **Source**: Created from `dev`
- **Merges**: Merged back to `dev` via pull request
- **Naming**: `feature/descriptive-name` or `feat/descriptive-name`
- **Lifespan**: Short-lived (delete after merge)
- **Examples**:
  - `feature/user-authentication`
  - `feat/git-commit-plugin`

### Fix Branches
- **Purpose**: Bug fixes and corrections
- **Source**: Created from `dev`
- **Merges**: Merged back to `dev` via pull request
- **Naming**: `fix/descriptive-name` or `bugfix/descriptive-name`
- **Lifespan**: Short-lived (delete after merge)
- **Examples**:
  - `fix/test-failures`
  - `fix/import-errors`

### Refactor Branches
- **Purpose**: Code restructuring without changing functionality
- **Source**: Created from `dev`
- **Merges**: Merged back to `dev` via pull request
- **Naming**: `refactor/descriptive-name`
- **Lifespan**: Short-lived (delete after merge)
- **Examples**:
  - `refactor/session-management`
  - `refactor/plugin-structure`

### Hotfix Branches
- **Purpose**: Critical fixes that need immediate attention
- **Source**: Created from the branch that needs fixing (usually `main` or `dev`)
- **Merges**:
  - If fixing `main`: Merge to both `main` AND `dev`
  - If fixing `dev`: Merge to `dev` only
- **Naming**: `hotfix/descriptive-name`
- **Lifespan**: Very short-lived (delete after merge)
- **Examples**:
  - `hotfix/security-vulnerability`
  - `hotfix/critical-crash`

## Workflow Examples

### Standard Feature Development

```bash
# Start from dev
git checkout dev
git pull origin dev

# Create feature branch
git checkout -b feature/new-awesome-feature

# Work, commit, push
git add .
git commit -m "feat: implement awesome feature"
git push -u origin feature/new-awesome-feature

# Create PR to dev
gh pr create --base dev --head feature/new-awesome-feature

# After merge, delete branch
git branch -d feature/new-awesome-feature
git push origin --delete feature/new-awesome-feature
```

### Release to Production

```bash
# Ensure dev is ready
git checkout dev
git pull origin dev

# Run all tests and validation
pytest
# ... verify everything works

# Create PR from dev to main
gh pr create --base main --head dev --title "Release v1.2.0"

# After merge, tag the release
git checkout main
git pull origin main
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
```

### Hotfix for Production

```bash
# Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# Fix the issue
git add .
git commit -m "fix: patch security vulnerability"
git push -u origin hotfix/critical-security-fix

# Create PR to main
gh pr create --base main --head hotfix/critical-security-fix

# IMPORTANT: Also merge to dev to keep in sync
git checkout dev
git pull origin dev
git merge hotfix/critical-security-fix
git push origin dev

# After both merges, delete hotfix branch
git branch -d hotfix/critical-security-fix
git push origin --delete hotfix/critical-security-fix

# Tag the hotfix release
git checkout main
git pull origin main
git tag -a v1.2.1 -m "Hotfix: Security patch"
git push origin v1.2.1
```

## Rules and Best Practices

### DO ✅

1. **Always create development branches from `dev`**
   ```bash
   git checkout dev && git pull && git checkout -b feature/my-feature
   ```

2. **Keep commits atomic and well-described**
   - Use Conventional Commits format: `type(scope): description`
   - Examples: `feat(auth): add OAuth2 support`, `fix(api): handle null responses`

3. **Pull request before merging to `dev`**
   - Allows for code review
   - Runs CI/CD checks
   - Documents changes

4. **Delete branches after merging**
   - Keeps repository clean
   - Prevents confusion about active work

5. **Tag all releases on `main`**
   - Use semantic versioning: `v1.2.3`
   - Include release notes in tag message

6. **Keep `dev` and `main` in sync**
   - `dev` should always be ahead or equal to `main`
   - Never commit directly to `main`

### DON'T ❌

1. **Never push directly to `main`**
   - Always use pull requests from `dev`
   - Branch protection enforces this

2. **Never create feature branches from `main`**
   - Always branch from `dev`
   - Ensures latest development changes are included

3. **Never force push to `main` or `dev`**
   - Rewrites history for other developers
   - Can lose work

4. **Never merge `main` into `dev`**
   - Flow should be: features → `dev` → `main`
   - Exception: Hotfixes that went directly to `main`

5. **Never leave stale branches**
   - Delete after merging
   - Clean up abandoned branches regularly

## Versioning Strategy

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version (`v2.0.0`): Incompatible API changes or breaking changes
- **MINOR** version (`v1.3.0`): New features, backwards-compatible
- **PATCH** version (`v1.2.5`): Bug fixes, backwards-compatible

### When to Bump Versions

- **MAJOR**: Breaking changes in plugin APIs, skill interfaces, or core workflows
- **MINOR**: New plugins, new features, new slash commands
- **PATCH**: Bug fixes, documentation updates, minor improvements

## Branch Protection Details

### `main` Branch Protection

The following protections are enforced on the `main` branch:

- ✅ Require pull request before merging
- ✅ Require linear history (no merge commits from command line)
- ✅ Prevent force pushes
- ✅ Prevent branch deletion
- ✅ No direct commits to `main`

These protections ensure that:
- All changes are reviewed
- History remains clean and linear
- Releases are intentional and documented
- Production code is stable

## Quick Reference

| Task | Command |
|------|---------|
| Start new feature | `git checkout dev && git pull && git checkout -b feature/name` |
| Commit changes | `git commit -m "type(scope): description"` |
| Push feature | `git push -u origin feature/name` |
| Create PR to dev | `gh pr create --base dev` |
| Merge dev to main | `gh pr create --base main --head dev` |
| Tag release | `git tag -a v1.2.3 -m "Release 1.2.3" && git push origin v1.2.3` |
| Delete branch locally | `git branch -d feature/name` |
| Delete branch remotely | `git push origin --delete feature/name` |

## Getting Help

- Branch naming unclear? Ask before creating
- Unsure about merge conflicts? Request help before force-pushing
- Need to undo something? Use `git reflog` to find the state, then reset

## Enforcement

Branch protection rules are configured via GitHub API and enforced automatically. Attempts to push directly to `main` or force-push will be rejected by GitHub.

---

Last updated: 2025-11-15
