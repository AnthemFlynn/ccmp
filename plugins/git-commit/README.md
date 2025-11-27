# git-commit

Professional git commit message generation following the Conventional Commits specification with automatic diff analysis.

## Description

The git-commit plugin helps developers write clear, professional commit messages that follow industry standards. It analyzes your staged changes automatically and suggests well-formatted commit messages following the [Conventional Commits](https://www.conventionalcommits.org/) specification.

**Key Features:**
- 🤖 Automatic diff analysis - analyzes staged changes and suggests commit type, scope, and description
- ✅ Commit message validation - ensures your commits follow the specification
- 📊 Changelog generation - creates formatted changelogs from commit history
- 🔢 Semantic versioning - automatically determines next version based on commits
- 🎯 Interactive mode - guides you through creating proper commits when needed

## Installation

This plugin is part of the [CCMP (Claude Code Marketplace Plugins)](https://github.com/AnthemFlynn/ccmp) repository.

### Install from CCMP Marketplace

```bash
# Add the CCMP marketplace
claude plugin marketplace add ccmp https://github.com/AnthemFlynn/ccmp

# Install the plugin
claude plugin install git-commit
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/AnthemFlynn/ccmp.git

# Link the plugin
claude plugin link ./ccmp/plugins/git-commit
```

## Usage

### Basic Commit Workflow

The most common use case - let the plugin analyze your changes and suggest a commit message:

```bash
# Stage your changes
git add .

# Run the analyzer
python3 plugins/git-commit/skills/git-commit/scripts/analyze-diff.py

# Output:
# 📊 Analyzed your changes:
#
# Files changed: 3
# Type: feat (100% confidence)
# Scope: auth
#
# 💡 Suggested commit:
#   feat(auth): add OAuth2 authentication
```

### Integration with Session Management

This plugin integrates automatically with the session-management plugin. When you create checkpoints, it will analyze your staged changes and generate professional commit messages:

```bash
# In your session
/session-management:checkpoint --commit --notes "Added user authentication"

# The plugin automatically:
# 1. Analyzes staged changes
# 2. Generates: feat(auth): add user authentication system
# 3. Adds your notes as commit body
# 4. Creates the commit
```

### Available Scripts

#### 1. Analyze Diff

Analyzes staged changes and suggests commit messages:

```bash
# Basic analysis
python3 scripts/analyze-diff.py

# JSON output (for programmatic use)
python3 scripts/analyze-diff.py --json

# Interactive commit
python3 scripts/analyze-diff.py --commit
```

**Example Output:**
```
📊 Analyzed your changes:

Files changed: 2
plugins/auth/oauth.py (+45 lines)
plugins/auth/middleware.py (+12 lines)

Changes: New OAuth authentication functions

Suggested commit:
  feat(auth): add OAuth2 authentication

To commit:
  git commit -m "feat(auth): add OAuth2 authentication"
```

#### 2. Validate Commit Message

Checks if a commit message follows the Conventional Commits specification:

```bash
# Validate a message
python3 scripts/validate.py "feat(api): add user endpoint"

# Output:
# ✅ Valid commit message
```

**Checks for:**
- Valid commit type (feat, fix, refactor, etc.)
- Proper format: `type(scope): description`
- Description is lowercase and imperative mood
- No trailing period
- Under 100 characters
- Breaking change indicator matches footer

#### 3. Generate Changelog

Creates a formatted changelog from git history:

```bash
# Generate changelog from last tag
python3 scripts/changelog.py

# Specify range
python3 scripts/changelog.py --from v1.0.0 --to HEAD

# Output to file
python3 scripts/changelog.py --output CHANGELOG.md
```

**Example Output:**
```markdown
# Changelog

## Features
- feat(auth): add OAuth2 authentication
- feat(api): add user management endpoints

## Bug Fixes
- fix(auth): handle expired tokens correctly
- fix(api): validate request parameters

## Breaking Changes
- feat(api)!: remove deprecated v1 endpoints
```

#### 4. Determine Next Version

Calculates the next semantic version based on commits:

```bash
# Check next version
python3 scripts/version.py

# Output:
# Current version: 1.2.3
# Next version: 2.0.0 (major bump due to breaking change)
```

**Version Bump Rules:**
- Breaking changes (`!` or `BREAKING CHANGE:`) → Major bump
- New features (`feat:`) → Minor bump
- Bug fixes (`fix:`) → Patch bump
- Other changes → Patch bump

## Commit Message Format

### Standard Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Commit Types

- `feat` - New feature for the user
- `fix` - Bug fix for the user
- `refactor` - Code change that neither fixes a bug nor adds a feature
- `perf` - Performance improvement
- `style` - Formatting, missing semi-colons, etc. (no code change)
- `test` - Adding or updating tests
- `docs` - Documentation only changes
- `build` - Changes to build system or dependencies
- `ops` - Infrastructure, deployment, CI/CD changes
- `chore` - Maintenance tasks, no production code change

### Scope

Optional context for the change (e.g., `api`, `auth`, `database`, `ui`). The analyzer automatically infers scope from file paths.

### Description

- Short summary (< 100 characters)
- Lowercase
- Imperative mood ("add" not "added")
- No period at the end

### Breaking Changes

Indicate breaking changes with `!` before the colon:

```
feat(api)!: remove deprecated v1 endpoints

BREAKING CHANGE: The v1 API endpoints have been removed.
Users must migrate to v2 endpoints. See migration guide.
```

## Examples

### Feature Addition

```bash
# You changed: src/auth/oauth.py (+50 lines)
# Analyzer suggests:
feat(auth): add OAuth2 authentication

Implements OAuth2 flow with Google and GitHub providers.
Includes token refresh and revocation.

Closes #123
```

### Bug Fix

```bash
# You changed: src/api/users.py (fix null check)
# Analyzer suggests:
fix(api): prevent null pointer in user lookup

Added null check before accessing user.profile to prevent
crashes when profile is not initialized.

Fixes #456
```

### Breaking Change

```bash
# You removed: src/api/v1/ directory
# Analyzer suggests:
feat(api)!: remove deprecated v1 endpoints

BREAKING CHANGE: All v1 API endpoints have been removed.
Users must migrate to v2. Migration guide: docs/v1-to-v2.md
```

### Refactoring

```bash
# You reorganized: src/utils/ modules
# Analyzer suggests:
refactor(utils): extract validation logic to separate module

Moved validation functions from utils.py to validators.py
for better organization. No functional changes.
```

## Integration

### With Session Management

The git-commit plugin integrates seamlessly with session-management:

```python
# In session.py checkpoint handler
analyzer_script = repo_root / "plugins" / "git-commit" / "skills" / "git-commit" / "scripts" / "analyze-diff.py"

result = subprocess.run(
    ["python3", str(analyzer_script), "--json"],
    capture_output=True,
    text=True
)

analysis = json.loads(result.stdout)
commit_msg = f"{analysis['type']}({analysis['scope']}): {analysis['description']}"
```

### As a Git Hook

Use as a commit-msg hook to validate all commits:

```bash
# In .git/hooks/commit-msg
#!/bin/bash
python3 plugins/git-commit/skills/git-commit/scripts/validate.py "$(cat $1)"
```

### In CI/CD

Validate commits in pull requests:

```yaml
# .github/workflows/validate-commits.yml
- name: Validate commit messages
  run: |
    for commit in $(git rev-list ${{ github.event.pull_request.base.sha }}..${{ github.sha }}); do
      msg=$(git log --format=%B -n 1 $commit)
      python3 scripts/validate.py "$msg" || exit 1
    done
```

## Configuration

The analyzer uses intelligent defaults based on file patterns and change analysis. No configuration required for basic usage.

### Customization

To customize scope detection, edit `analyze-diff.py`:

```python
SCOPE_PATTERNS = {
    r'.*/(auth|login|oauth)': 'auth',
    r'.*/(api|endpoints|routes)': 'api',
    r'.*/database|migrations': 'database',
    # Add your patterns here
}
```

## Troubleshooting

### No staged changes found

**Problem:** `Error: No staged changes found. Use: git add <files>`

**Solution:** Stage your changes first:
```bash
git add <files>
python3 scripts/analyze-diff.py
```

### Low confidence warning

**Problem:** `⚠️ Low confidence - please review and adjust`

**Solution:** The analyzer isn't sure about the commit type. Review the suggestion and adjust manually or use interactive mode:
```bash
python3 scripts/analyze-diff.py --commit
# Review and confirm or edit the suggestion
```

### Script not executable

**Problem:** `Permission denied` when running scripts

**Solution:** Make scripts executable:
```bash
chmod +x plugins/git-commit/skills/git-commit/scripts/*.py
```

## Contributing

Contributions welcome! This plugin is part of the CCMP repository.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run the analyzer on your changes: `python3 scripts/analyze-diff.py`
5. Commit using conventional format
6. Push and create a pull request

## License

MIT License - see LICENSE file for details

## Links

- **Repository:** https://github.com/AnthemFlynn/ccmp
- **Issues:** https://github.com/AnthemFlynn/ccmp/issues
- **Conventional Commits:** https://www.conventionalcommits.org/
- **Semantic Versioning:** https://semver.org/

## Credits

Author: AnthemFlynn (AnthemFlynn@users.noreply.github.com)

Part of the Claude Code Marketplace Plugins (CCMP) collection.
