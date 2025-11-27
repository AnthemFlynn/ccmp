# project-status-report

Generate comprehensive project health and status reports for rapid developer onboarding and context restoration.

## Description

The project-status-report plugin helps developers quickly understand the current state of a project. It's designed for rapid re-immersion after time away, providing a prioritized view of project health, git status, recent work, and open items.

**Key Features:**
- 🏥 Health indicators - test status, linting, coverage, build health
- 📍 Git analysis - branch status, uncommitted changes, sync state
- 📖 Recent activity - last checkpoint, accomplishments, where you left off
- 📋 Work items - session objectives, TODOs, FIXMEs in code
- 💡 AI suggestions - recommended next actions based on project state

## Installation

This plugin is part of the [CCMP (Claude Code Marketplace Plugins)](https://github.com/AnthemFlynn/ccmp) repository.

### Install from CCMP Marketplace

```bash
# Add the CCMP marketplace
claude plugin marketplace add ccmp https://github.com/AnthemFlynn/ccmp

# Install the plugin
claude plugin install project-status-report
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/AnthemFlynn/ccmp.git

# Link the plugin
claude plugin link ./ccmp/plugins/project-status-report
```

## Usage

### As a Slash Command

The easiest way to use this plugin is through Claude Code:

```
/project-status-report:project-report
```

Claude will generate a comprehensive status report and present it in the conversation.

### Standalone Script

Generate a report from the command line:

```bash
# Generate report for current directory
python3 plugins/project-status-report/skills/project-status-report/scripts/report.py

# Generate report for specific project
python3 scripts/report.py --path /path/to/project

# Save report to file
python3 scripts/report.py --output status-report.md
```

### Integrated with Session Management

The plugin integrates automatically with session-management. When you start a session, it generates a project status report:

```bash
/session-management:session-start

# Automatically generates and displays:
# - Project health check
# - Git status
# - Open work items
# - Recommended next actions
```

### Programmatic Usage

Import and use in your own scripts:

```python
from report import ReportGenerator

generator = ReportGenerator(project_path=".")
report_text = generator.generate()
print(report_text)
```

## Report Structure

The report is organized by priority, with the most critical information first:

### 1. Health Indicators 🏥

```
=== PROJECT HEALTH ===

Tests: ✅ 24 passed, 0 failed
Build: ✅ Success (2.3s)
Linting: ⚠️ 3 warnings
Coverage: 85% (target: 80%)
```

**Checks:**
- Test results (pytest, jest, etc.)
- Build status
- Linting errors/warnings
- Code coverage
- Context health (if claude-context-manager installed)

### 2. Git Status 📍

```
=== GIT STATUS ===

Branch: feature/user-auth
Status: 3 files changed, 45 insertions, 12 deletions
Staged: 2 files
Remote: 2 commits ahead, sync recommended

Active Branches:
- feature/user-auth (current, last commit 2h ago)
- fix/validation-bug (last commit 1d ago)
- main (up to date with origin)
```

**Information:**
- Current branch name
- Uncommitted/staged changes
- Commits ahead/behind remote
- Recently active branches

### 3. Recent Activity 📖

```
=== RECENT WORK ===

Last Checkpoint: 2025-11-14 15:30
- Implemented OAuth2 authentication flow
- Added token refresh mechanism
- Updated user model with OAuth fields

Status: GREEN (tests passing)
```

**Shows:**
- Most recent checkpoint or commit
- What was accomplished
- Session status (if using session-management)
- Where work was left off

### 4. Open Work Items 📋

```
=== OPEN WORK ===

Session Objectives:
- Complete user authentication system
- Add integration tests for auth flow

Code TODOs (5):
- src/auth/oauth.py:45 - TODO: Add token expiration handling
- src/auth/middleware.py:12 - TODO: Implement rate limiting
- ...

FIXMEs (2):
- src/api/users.py:89 - FIXME: Handle edge case for deleted users
- ...
```

**Scans for:**
- Active session objectives
- TODO comments in code
- FIXME comments in code
- Locations and descriptions

### 5. AI Suggestions 💡

```
=== RECOMMENDED NEXT ACTIONS ===

Based on your project state:

1. Complete auth integration tests (30-45 min)
   - You have working OAuth flow
   - Tests will validate edge cases
   - Priority: HIGH

2. Address token expiration TODO (15-20 min)
   - Critical for security
   - Implementation is straightforward
   - Priority: HIGH

3. Review and update context docs (10 min)
   - Context files are 15 days old
   - Quick refresh recommended
   - Priority: MEDIUM
```

**Provides:**
- Contextual recommendations
- Time estimates
- Priority levels
- Reasoning for suggestions

## Example Output

Here's a complete example of what the report looks like:

```markdown
======================================================================
PROJECT STATUS REPORT
Generated: 2025-11-15 10:30:00
Project: /Users/dev/my-project
======================================================================

=== PROJECT HEALTH ===

✅ Tests: 24 passed, 0 failed (100%)
✅ Build: Success (2.3s)
⚠️  Linting: 3 warnings
✅ Coverage: 85% (target: 80%)
✅ Context: Healthy (updated 3 days ago)

Health Score: 9/10 (EXCELLENT)

=== GIT STATUS ===

Branch: feature/user-auth
Status: Clean working directory
Staged: 0 files
Remote: 2 commits ahead of origin/feature/user-auth

Active Branches (last 7 days):
- feature/user-auth (current) - last activity 2h ago
- fix/validation-bug - last activity 1d ago
- main (synced with origin)

=== RECENT WORK ===

Last Checkpoint: 2025-11-14 15:30 (19h ago)

Accomplished:
- Implemented OAuth2 authentication flow with Google/GitHub
- Added token refresh and revocation mechanisms
- Updated user model to store OAuth provider info
- Added integration with existing session system

Status: GREEN (all tests passing)
TDD Phase: REFACTOR

Next: Add integration tests for OAuth edge cases

=== OPEN WORK ===

Session Objectives:
✓ Implement OAuth2 authentication
✓ Add token refresh
○ Write integration tests
○ Update documentation

Code TODOs (5 found):
1. src/auth/oauth.py:45
   TODO: Add token expiration handling

2. src/auth/middleware.py:12
   TODO: Implement rate limiting for auth endpoints

3. src/api/users.py:23
   TODO: Add OAuth provider to user API response

4. tests/auth/test_oauth.py:67
   TODO: Add test for token refresh edge case

5. docs/api.md:112
   TODO: Document OAuth endpoints

FIXMEs (2 found):
1. src/api/users.py:89
   FIXME: Handle edge case when user deletes account mid-OAuth

2. src/auth/oauth.py:123
   FIXME: Improve error messaging for invalid tokens

=== RECOMMENDED NEXT ACTIONS ===

Based on current project state, here are suggested next steps:

1. Write OAuth integration tests (HIGH PRIORITY)
   Estimated time: 30-45 minutes
   Reasoning: Core feature complete, needs test coverage

   What to do:
   - Test full OAuth flow (Google and GitHub)
   - Test token refresh mechanism
   - Test error cases (invalid tokens, expired tokens)
   - Test OAuth provider switching

2. Address token expiration TODO (HIGH PRIORITY)
   Estimated time: 15-20 minutes
   Reasoning: Security-critical, straightforward implementation

   Location: src/auth/oauth.py:45

3. Update API documentation (MEDIUM PRIORITY)
   Estimated time: 15 minutes
   Reasoning: New OAuth endpoints need documentation

   Location: docs/api.md:112

4. Handle user deletion edge case (MEDIUM PRIORITY)
   Estimated time: 20-30 minutes
   Reasoning: Rare but important edge case

   Location: src/api/users.py:89

5. Review context health (LOW PRIORITY)
   Estimated time: 10 minutes
   Reasoning: Context was updated recently, quick check recommended

======================================================================
END OF REPORT
======================================================================
```

## Integration

### With Session Management

Automatic integration when both plugins are installed:

```python
# In session start
from report import ReportGenerator

def cmd_start(args):
    try:
        generator = ReportGenerator()
        report = generator.generate()
        print(report)
    except ImportError:
        print("⚠️  project-status-report plugin not found")

    # Continue with session start...
```

### With Claude Context Manager

The report includes context health when claude-context-manager is installed:

```python
# Automatically checks
context_health = check_context_freshness()
# Reports if context files are stale
```

### As a Pre-Commit Hook

Use to check project health before commits:

```bash
# .git/hooks/pre-commit
#!/bin/bash
python3 plugins/project-status-report/scripts/report.py --health-only
if [ $? -ne 0 ]; then
    echo "Health check failed"
    exit 1
fi
```

## Available Scripts

### 1. Git Analysis (`git_analysis.py`)

Analyzes git repository state:

```python
from git_analysis import GitAnalyzer

analyzer = GitAnalyzer()

# Get current branch
branch = analyzer.get_current_branch()

# Get uncommitted changes
changes = analyzer.get_uncommitted_changes()
# Returns: {'modified': [], 'staged': [], 'untracked': []}

# Get active branches
branches = analyzer.get_active_branches(days=7)
```

### 2. Health Check (`health_check.py`)

Checks project health indicators:

```python
from health_check import HealthChecker

checker = HealthChecker()

# Check tests
test_status = checker.check_tests()
# Returns: {'passing': 24, 'failing': 0, 'total': 24}

# Generate health report
report = checker.generate_report()
```

### 3. Work Items Scanner (`work_items.py`)

Scans code for TODOs and FIXMEs:

```python
from work_items import WorkItemsScanner

scanner = WorkItemsScanner()

# Scan for TODOs
todos = scanner.scan_code_markers(marker='TODO')
# Returns: [{'file': 'path.py', 'line': 45, 'text': 'Add validation'}]

# Load session objectives
objectives = scanner.load_session_objectives()
```

### 4. Main Report Generator (`report.py`)

Integrates all components:

```python
from report import ReportGenerator

generator = ReportGenerator(project_path=".")

# Generate full report
report = generator.generate()

# Generate specific section
health_only = generator.generate_health_section()
```

## Configuration

No configuration required for basic usage. The plugin automatically:
- Detects test framework (pytest, jest, etc.)
- Finds project root via git
- Scans for TODO/FIXME markers
- Integrates with other CCMP plugins

### Optional: Custom Markers

To scan for custom markers, edit `work_items.py`:

```python
# Add custom markers
MARKERS = ['TODO', 'FIXME', 'HACK', 'OPTIMIZE', 'REVIEW']
```

## Troubleshooting

### "Not in a git repository"

**Problem:** Plugin requires git repository

**Solution:** Initialize git or run from within a git repo:
```bash
git init
# or
cd /path/to/git/repo
```

### "No tests found"

**Problem:** Plugin can't detect test framework

**Solution:** Ensure tests are in standard locations:
- Python: `tests/` or `test_*.py`
- JavaScript: `__tests__/` or `*.test.js`

### Script permission errors

**Problem:** `Permission denied` when running scripts

**Solution:** Make scripts executable:
```bash
chmod +x plugins/project-status-report/skills/project-status-report/scripts/*.py
```

## Testing

The plugin includes comprehensive tests:

```bash
# Run all tests
pytest plugins/project-status-report/skills/project-status-report/scripts/

# Run specific test file
pytest test_git_analysis.py
pytest test_health_check.py
pytest test_report.py
pytest test_work_items.py
```

**Test Coverage:**
- Git analysis: branch detection, change tracking, active branches
- Health checking: test status, build health
- Work items: TODO/FIXME scanning, objective loading
- Report generation: full report assembly

## Contributing

Contributions welcome! This plugin is part of the CCMP repository.

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Links

- **Repository:** https://github.com/AnthemFlynn/ccmp
- **Issues:** https://github.com/AnthemFlynn/ccmp/issues
- **Documentation:** See `SKILL.md` for integration details

## Credits

Author: AnthemFlynn (AnthemFlynn@users.noreply.github.com)

Part of the Claude Code Marketplace Plugins (CCMP) collection.
