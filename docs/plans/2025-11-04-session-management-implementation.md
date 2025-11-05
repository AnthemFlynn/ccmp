# Session Management Refactoring Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal**: Build git-native session onboarding system that minimizes context-switching time for developers

**Architecture**: Two-skill system - project-status-report (new standalone) + session-management (refactored). Observer pattern for superpowers integration. Project-local storage (.sessions/).

**Tech Stack**: Python 3.13, Git, Markdown templates, JSON state files, .ccmp plugin integration

---

## Phase 1: Project Status Report Skill

### Task 1: Create Plugin Structure

**Files:**
- Create: `plugins/project-status-report/.claude-plugin/plugin.json`
- Create: `plugins/project-status-report/skills/project-status-report/SKILL.md`
- Create: `plugins/project-status-report/commands/project-report.md`

**Step 1: Create directory structure**

```bash
mkdir -p plugins/project-status-report/.claude-plugin
mkdir -p plugins/project-status-report/skills/project-status-report/scripts
mkdir -p plugins/project-status-report/skills/project-status-report/templates
mkdir -p plugins/project-status-report/commands
```

Run: `ls -la plugins/project-status-report/`
Expected: Directory structure created

**Step 2: Write plugin.json manifest**

Create `plugins/project-status-report/.claude-plugin/plugin.json`:

```json
{
  "name": "project-status-report",
  "version": "1.0.0",
  "description": "Generate comprehensive project health and status reports for rapid developer onboarding",
  "author": {
    "name": "AnthemFlynn",
    "email": "AnthemFlynn@users.noreply.github.com"
  },
  "repository": "https://github.com/AnthemFlynn/skills",
  "license": "MIT",
  "keywords": ["reporting", "project-status", "health-check", "git-analysis", "onboarding"]
}
```

**Step 3: Verify plugin structure**

Run: `claude plugin validate plugins/project-status-report`
Expected: Validation passes

**Step 4: Commit plugin structure**

```bash
git add plugins/project-status-report/
git commit -m "feat(project-status-report): add plugin structure and manifest"
```

### Task 2: Git Analysis Module

**Files:**
- Create: `plugins/project-status-report/skills/project-status-report/scripts/git_analysis.py`
- Create: `plugins/project-status-report/skills/project-status-report/scripts/__init__.py`

**Step 1: Write test for git status analysis**

Create `plugins/project-status-report/skills/project-status-report/scripts/test_git_analysis.py`:

```python
import pytest
from git_analysis import GitAnalyzer

def test_get_current_branch():
    """Test that we can get current git branch"""
    analyzer = GitAnalyzer()
    branch = analyzer.get_current_branch()
    assert branch is not None
    assert isinstance(branch, str)
    assert len(branch) > 0

def test_get_uncommitted_changes():
    """Test detection of uncommitted changes"""
    analyzer = GitAnalyzer()
    changes = analyzer.get_uncommitted_changes()
    assert isinstance(changes, dict)
    assert "modified" in changes
    assert "untracked" in changes
    assert isinstance(changes["modified"], list)
    assert isinstance(changes["untracked"], list)

def test_get_active_branches():
    """Test listing active branches with recent activity"""
    analyzer = GitAnalyzer()
    branches = analyzer.get_active_branches(limit=5)
    assert isinstance(branches, list)
    assert len(branches) <= 5
    for branch in branches:
        assert "name" in branch
        assert "last_commit" in branch
        assert "last_activity" in branch
```

**Step 2: Run tests to verify they fail**

Run: `cd plugins/project-status-report/skills/project-status-report/scripts && pytest test_git_analysis.py -v`
Expected: FAIL with "No module named 'git_analysis'"

**Step 3: Write minimal GitAnalyzer implementation**

Create `plugins/project-status-report/skills/project-status-report/scripts/git_analysis.py`:

```python
#!/usr/bin/env python3
"""
Git Analysis Module

Analyzes git repository state for project status reports.
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class GitAnalyzer:
    """Analyze git repository state"""

    def __init__(self, repo_path: str = "."):
        """Initialize analyzer with repository path"""
        self.repo_path = Path(repo_path)

    def _run_git(self, args: List[str]) -> Optional[str]:
        """Run git command and return output"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def get_current_branch(self) -> Optional[str]:
        """Get current git branch name"""
        return self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])

    def get_uncommitted_changes(self) -> Dict[str, List[str]]:
        """Get uncommitted and untracked files"""
        # Get modified files
        modified_output = self._run_git(["diff", "--name-only"])
        modified = modified_output.split("\n") if modified_output else []
        modified = [f for f in modified if f]  # Filter empty strings

        # Get untracked files
        untracked_output = self._run_git(["ls-files", "--others", "--exclude-standard"])
        untracked = untracked_output.split("\n") if untracked_output else []
        untracked = [f for f in untracked if f]

        return {
            "modified": modified,
            "untracked": untracked
        }

    def get_active_branches(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get branches sorted by recent activity"""
        # Get all branches with last commit info
        output = self._run_git([
            "for-each-ref",
            "--sort=-committerdate",
            "--format=%(refname:short)|%(committerdate:relative)|%(subject)",
            "refs/heads/",
            f"--count={limit}"
        ])

        if not output:
            return []

        branches = []
        for line in output.split("\n"):
            if not line:
                continue
            parts = line.split("|", 2)
            if len(parts) == 3:
                branches.append({
                    "name": parts[0],
                    "last_activity": parts[1],
                    "last_commit": parts[2]
                })

        return branches

    def get_remote_sync_status(self) -> Dict[str, any]:
        """Get sync status with remote"""
        current_branch = self.get_current_branch()
        if not current_branch:
            return {"error": "Not in a git repository"}

        # Get ahead/behind count
        upstream = self._run_git(["rev-parse", "--abbrev-ref", f"{current_branch}@{{upstream}}"])

        if not upstream:
            return {"status": "no_upstream"}

        # Get ahead/behind counts
        ahead_behind = self._run_git(["rev-list", "--left-right", "--count", f"{upstream}...HEAD"])

        if ahead_behind:
            parts = ahead_behind.split("\t")
            behind = int(parts[0])
            ahead = int(parts[1])

            return {
                "upstream": upstream,
                "ahead": ahead,
                "behind": behind
            }

        return {"status": "unknown"}

    def generate_report(self) -> str:
        """Generate git status section of report"""
        current_branch = self.get_current_branch()
        changes = self.get_uncommitted_changes()
        sync_status = self.get_remote_sync_status()
        active_branches = self.get_active_branches(limit=5)

        lines = []
        lines.append("## 📍 Git Status")
        lines.append("")
        lines.append(f"**Current Branch**: {current_branch or 'Unknown'}")

        # Sync status
        if "upstream" in sync_status:
            ahead = sync_status["ahead"]
            behind = sync_status["behind"]
            if ahead > 0 and behind > 0:
                lines.append(f"**Status**: {ahead} commits ahead, {behind} commits behind {sync_status['upstream']}")
            elif ahead > 0:
                lines.append(f"**Status**: {ahead} commits ahead of {sync_status['upstream']}")
            elif behind > 0:
                lines.append(f"**Status**: {behind} commits behind {sync_status['upstream']}")
            else:
                lines.append(f"**Status**: Up to date with {sync_status['upstream']}")

        # Uncommitted changes
        if changes["modified"]:
            lines.append(f"**Uncommitted**: {len(changes['modified'])} files modified")
        if changes["untracked"]:
            lines.append(f"**Untracked**: {len(changes['untracked'])} files")

        lines.append("")
        lines.append("**Active Branches** (recent):")
        for branch in active_branches:
            marker = "(current)" if branch["name"] == current_branch else ""
            lines.append(f"- {branch['name']} {marker} (last commit: {branch['last_activity']})")

        return "\n".join(lines)
```

Create `plugins/project-status-report/skills/project-status-report/scripts/__init__.py` (empty file)

**Step 4: Run tests to verify they pass**

Run: `cd plugins/project-status-report/skills/project-status-report/scripts && pytest test_git_analysis.py -v`
Expected: PASS (all tests green)

**Step 5: Commit git analysis module**

```bash
git add plugins/project-status-report/skills/project-status-report/scripts/git_analysis.py
git add plugins/project-status-report/skills/project-status-report/scripts/__init__.py
git add plugins/project-status-report/skills/project-status-report/scripts/test_git_analysis.py
git commit -m "feat(project-status-report): add git analysis module with tests"
```

### Task 3: Health Check Module

**Files:**
- Create: `plugins/project-status-report/skills/project-status-report/scripts/health_check.py`
- Create: `plugins/project-status-report/skills/project-status-report/scripts/test_health_check.py`

**Step 1: Write test for health checks**

Create `plugins/project-status-report/skills/project-status-report/scripts/test_health_check.py`:

```python
import pytest
from health_check import HealthChecker

def test_check_tests_basic():
    """Test that we can check test status"""
    checker = HealthChecker()
    result = checker.check_tests()
    assert "status" in result
    assert result["status"] in ["pass", "fail", "unknown"]

def test_generate_report():
    """Test health report generation"""
    checker = HealthChecker()
    report = checker.generate_report()
    assert isinstance(report, str)
    assert "Health Indicators" in report
```

**Step 2: Run tests to verify they fail**

Run: `cd plugins/project-status-report/skills/project-status-report/scripts && pytest test_health_check.py -v`
Expected: FAIL with "No module named 'health_check'"

**Step 3: Write HealthChecker implementation**

Create `plugins/project-status-report/skills/project-status-report/scripts/health_check.py`:

```python
#!/usr/bin/env python3
"""
Health Check Module

Checks project health: tests, linting, coverage, build status.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional


class HealthChecker:
    """Check project health indicators"""

    def __init__(self, project_path: str = "."):
        """Initialize checker with project path"""
        self.project_path = Path(project_path)

    def _run_command(self, cmd: List[str]) -> Optional[subprocess.CompletedProcess]:
        """Run command and return result"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def check_tests(self) -> Dict[str, any]:
        """Check test status (pytest)"""
        result = self._run_command(["pytest", "--collect-only", "-q"])

        if not result:
            return {"status": "unknown", "reason": "pytest not found"}

        # Check if pytest runs successfully
        if result.returncode == 0:
            # Parse output for test count
            lines = result.stdout.split("\n")
            for line in lines:
                if "test" in line.lower():
                    return {"status": "pass", "message": line.strip()}
            return {"status": "pass"}
        else:
            return {"status": "fail", "message": result.stderr[:200]}

    def check_ccmp_context_health(self) -> Optional[Dict[str, any]]:
        """Check context health from .ccmp/state.json"""
        state_file = self.project_path / ".ccmp" / "state.json"

        if not state_file.exists():
            return None

        try:
            with open(state_file) as f:
                state = json.load(f)

            context_state = state.get("claude-context-manager", {})
            if context_state:
                return {
                    "health_score": context_state.get("health_score"),
                    "critical_files": context_state.get("critical_files", [])
                }
        except (json.JSONDecodeError, IOError):
            pass

        return None

    def generate_report(self) -> str:
        """Generate health indicators section"""
        lines = []
        lines.append("## 🏥 Health Indicators")
        lines.append("")

        # Test status
        test_result = self.check_tests()
        if test_result["status"] == "pass":
            lines.append(f"✅ Tests: {test_result.get('message', 'Passing')}")
        elif test_result["status"] == "fail":
            lines.append(f"❌ Tests: {test_result.get('message', 'Failing')}")
        else:
            lines.append("⚠️  Tests: Status unknown")

        # Context health (if available)
        context_health = self.check_ccmp_context_health()
        if context_health:
            score = context_health.get("health_score")
            critical = context_health.get("critical_files", [])
            if score is not None:
                if score >= 80:
                    lines.append(f"✅ Context Health: {score}/100")
                elif score >= 60:
                    lines.append(f"⚠️  Context Health: {score}/100")
                else:
                    lines.append(f"❌ Context Health: {score}/100")

            if critical:
                lines.append(f"⚠️  Context: {len(critical)} files need attention")

        # Summary
        lines.append("")
        critical_issues = [line for line in lines if "❌" in line]
        warnings = [line for line in lines if "⚠️" in line]

        if critical_issues:
            lines.append(f"**Critical Issues**: {len(critical_issues)}")
        if warnings:
            lines.append(f"**Warnings**: {len(warnings)}")

        return "\n".join(lines)
```

**Step 4: Run tests to verify they pass**

Run: `cd plugins/project-status-report/skills/project-status-report/scripts && pytest test_health_check.py -v`
Expected: PASS

**Step 5: Commit health check module**

```bash
git add plugins/project-status-report/skills/project-status-report/scripts/health_check.py
git add plugins/project-status-report/skills/project-status-report/scripts/test_health_check.py
git commit -m "feat(project-status-report): add health check module with tests"
```

### Task 4: Work Items Scanner

**Files:**
- Create: `plugins/project-status-report/skills/project-status-report/scripts/work_items.py`
- Create: `plugins/project-status-report/skills/project-status-report/scripts/test_work_items.py`

**Step 1: Write test for TODO/FIXME scanning**

Create `plugins/project-status-report/skills/project-status-report/scripts/test_work_items.py`:

```python
import pytest
from pathlib import Path
from work_items import WorkItemsScanner

def test_scan_code_markers():
    """Test scanning code for TODO/FIXME markers"""
    scanner = WorkItemsScanner()
    markers = scanner.scan_code_markers()
    assert isinstance(markers, dict)
    assert "todos" in markers
    assert "fixmes" in markers

def test_load_session_objectives():
    """Test loading objectives from session state"""
    scanner = WorkItemsScanner()
    objectives = scanner.load_session_objectives()
    # Should return list even if file doesn't exist
    assert isinstance(objectives, list)
```

**Step 2: Run tests to verify they fail**

Run: `cd plugins/project-status-report/skills/project-status-report/scripts && pytest test_work_items.py -v`
Expected: FAIL with "No module named 'work_items'"

**Step 3: Write WorkItemsScanner implementation**

Create `plugins/project-status-report/skills/project-status-report/scripts/work_items.py`:

```python
#!/usr/bin/env python3
"""
Work Items Scanner

Scans code for TODOs, FIXMEs, and loads session objectives.
"""

import re
import json
from pathlib import Path
from typing import Dict, List


class WorkItemsScanner:
    """Scan project for work items"""

    def __init__(self, project_path: str = "."):
        """Initialize scanner with project path"""
        self.project_path = Path(project_path)

    def scan_code_markers(self, patterns: List[str] = None) -> Dict[str, List[Dict]]:
        """Scan code files for TODO/FIXME markers"""
        if patterns is None:
            patterns = ["*.py", "*.js", "*.ts", "*.tsx", "*.java", "*.go", "*.rs"]

        todos = []
        fixmes = []

        for pattern in patterns:
            for file_path in self.project_path.rglob(pattern):
                # Skip test files and node_modules
                if "test" in str(file_path) or "node_modules" in str(file_path):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            # Match TODO: or TODO -
                            if re.search(r'TODO[:\-]', line, re.IGNORECASE):
                                comment = line.strip()
                                todos.append({
                                    "file": str(file_path.relative_to(self.project_path)),
                                    "line": line_num,
                                    "text": comment
                                })
                            # Match FIXME: or FIXME -
                            if re.search(r'FIXME[:\-]', line, re.IGNORECASE):
                                comment = line.strip()
                                fixmes.append({
                                    "file": str(file_path.relative_to(self.project_path)),
                                    "line": line_num,
                                    "text": comment
                                })
                except (IOError, UnicodeDecodeError):
                    # Skip files we can't read
                    continue

        return {
            "todos": todos[:20],  # Limit to first 20
            "fixmes": fixmes[:20]
        }

    def load_session_objectives(self) -> List[Dict]:
        """Load objectives from .sessions/state.json"""
        state_file = self.project_path / ".sessions" / "state.json"

        if not state_file.exists():
            return []

        try:
            with open(state_file) as f:
                state = json.load(f)

            objectives = state.get("objectives", [])
            # Convert to list of dicts if it's a simple list
            if objectives and isinstance(objectives[0], str):
                return [{"text": obj, "completed": False} for obj in objectives]

            return objectives
        except (json.JSONDecodeError, IOError, KeyError):
            return []

    def generate_report(self) -> str:
        """Generate work items section"""
        lines = []
        lines.append("## 📋 Open Work Items")
        lines.append("")

        # Session objectives
        objectives = self.load_session_objectives()
        if objectives:
            lines.append("**Session Objectives**:")
            for obj in objectives:
                status = "[x]" if obj.get("completed") else "[ ]"
                text = obj.get("text", "Unknown objective")
                lines.append(f"- {status} {text}")
            lines.append("")

        # Code markers
        markers = self.scan_code_markers()
        todos = markers["todos"]
        fixmes = markers["fixmes"]

        if todos:
            lines.append("**TODOs in Code**:")
            for todo in todos[:5]:  # Show first 5
                lines.append(f"- {todo['file']}:{todo['line']} - {todo['text'][:80]}")
            if len(todos) > 5:
                lines.append(f"- ... and {len(todos) - 5} more")
            lines.append("")

        if fixmes:
            lines.append("**FIXMEs in Code**:")
            for fixme in fixmes[:5]:
                lines.append(f"- {fixme['file']}:{fixme['line']} - {fixme['text'][:80]}")
            if len(fixmes) > 5:
                lines.append(f"- ... and {len(fixmes) - 5} more")
            lines.append("")

        lines.append(f"**Summary**: {len(todos)} TODOs, {len(fixmes)} FIXMEs")

        return "\n".join(lines)
```

**Step 4: Run tests to verify they pass**

Run: `cd plugins/project-status-report/skills/project-status-report/scripts && pytest test_work_items.py -v`
Expected: PASS

**Step 5: Commit work items scanner**

```bash
git add plugins/project-status-report/skills/project-status-report/scripts/work_items.py
git add plugins/project-status-report/skills/project-status-report/scripts/test_work_items.py
git commit -m "feat(project-status-report): add work items scanner with tests"
```

### Task 5: Main Report Generator

**Files:**
- Create: `plugins/project-status-report/skills/project-status-report/scripts/report.py`
- Create: `plugins/project-status-report/skills/project-status-report/scripts/test_report.py`

**Step 1: Write test for report generator**

Create `plugins/project-status-report/skills/project-status-report/scripts/test_report.py`:

```python
import pytest
from report import ReportGenerator

def test_generate_full_report():
    """Test generating complete project status report"""
    generator = ReportGenerator()
    report = generator.generate()

    assert isinstance(report, str)
    assert "Project Status Report" in report
    assert "Health Indicators" in report
    assert "Git Status" in report
    assert "Open Work Items" in report
```

**Step 2: Run tests to verify they fail**

Run: `cd plugins/project-status-report/skills/project-status-report/scripts && pytest test_report.py -v`
Expected: FAIL with "No module named 'report'"

**Step 3: Write ReportGenerator implementation**

Create `plugins/project-status-report/skills/project-status-report/scripts/report.py`:

```python
#!/usr/bin/env python3
"""
Project Status Report Generator

Main CLI for generating comprehensive project status reports.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from health_check import HealthChecker
from git_analysis import GitAnalyzer
from work_items import WorkItemsScanner


class ReportGenerator:
    """Generate comprehensive project status reports"""

    def __init__(self, project_path: str = "."):
        """Initialize generator with project path"""
        self.project_path = Path(project_path)
        self.health_checker = HealthChecker(project_path)
        self.git_analyzer = GitAnalyzer(project_path)
        self.work_scanner = WorkItemsScanner(project_path)

    def load_recent_session(self) -> str:
        """Load recent session summary from checkpoints"""
        checkpoints_dir = self.project_path / ".sessions" / "checkpoints"

        if not checkpoints_dir.exists():
            return "**No previous sessions found**"

        # Get most recent checkpoint
        checkpoints = sorted(checkpoints_dir.glob("*.md"), reverse=True)
        if not checkpoints:
            return "**No checkpoints found**"

        latest = checkpoints[0]

        # Read first few lines for summary
        try:
            with open(latest) as f:
                lines = f.readlines()[:15]

            summary = f"**Last Checkpoint**: {latest.stem}\n\n"
            summary += "".join(lines)
            return summary
        except IOError:
            return "**Error reading checkpoint**"

    def generate(self) -> str:
        """Generate complete project status report"""
        lines = []
        lines.append("# Project Status Report")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Priority 1: Health Indicators
        lines.append(self.health_checker.generate_report())
        lines.append("")

        # Priority 2: Git Status
        lines.append(self.git_analyzer.generate_report())
        lines.append("")

        # Priority 3: Recent Session
        lines.append("## 📖 Recent Session")
        lines.append("")
        lines.append(self.load_recent_session())
        lines.append("")

        # Priority 4: Open Work Items
        lines.append(self.work_scanner.generate_report())
        lines.append("")

        # Priority 5: Backlog (placeholder)
        lines.append("## 📚 Backlog")
        lines.append("")
        lines.append("*No backlog configured*")
        lines.append("")

        # Priority 6: AI Suggestions (placeholder)
        lines.append("## 💡 Suggested Next Actions")
        lines.append("")
        lines.append("*AI suggestions will be generated based on above analysis*")
        lines.append("")

        return "\n".join(lines)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Generate project status report")
    parser.add_argument("--path", default=".", help="Project path (default: current directory)")
    parser.add_argument("--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    generator = ReportGenerator(args.path)
    report = generator.generate()

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Step 4: Run tests to verify they pass**

Run: `cd plugins/project-status-report/skills/project-status-report/scripts && pytest test_report.py -v`
Expected: PASS

**Step 5: Test CLI manually**

Run: `cd plugins/project-status-report/skills/project-status-report/scripts && python report.py`
Expected: Outputs project status report to stdout

**Step 6: Commit report generator**

```bash
git add plugins/project-status-report/skills/project-status-report/scripts/report.py
git add plugins/project-status-report/skills/project-status-report/scripts/test_report.py
git commit -m "feat(project-status-report): add main report generator CLI"
```

### Task 6: SKILL.md Documentation

**Files:**
- Create: `plugins/project-status-report/skills/project-status-report/SKILL.md`

**Step 1: Write SKILL.md**

Create `plugins/project-status-report/skills/project-status-report/SKILL.md`:

```markdown
---
name: project-status-report
description: Generate comprehensive project health and status reports for rapid developer onboarding. Use when starting sessions, checking project health mid-work, or needing overview of git status, open work items, and suggested next actions.
---

# Project Status Report

Generate comprehensive project health and status reports for rapid developer onboarding.

## When to Use

- **Session start**: Get full project context before deciding what to work on
- **Mid-session check**: Quick health check without session overhead
- **Context switching**: Rapid re-immersion after days away from project
- **Before major changes**: Understand current state before refactoring

## What It Reports

### Priority 1: Health Indicators 🏥
- Test status (passing/failing)
- Linting errors
- Coverage metrics
- Build status
- Context health (from claude-context-manager if available)

### Priority 2: Git Status 📍
- Current branch
- Uncommitted changes
- Sync status with remote
- Active branches (recent activity)

### Priority 3: Recent Session 📖
- Last checkpoint summary
- What was accomplished
- Where you left off

### Priority 4: Open Work Items 📋
- Session objectives
- TODOs in code
- FIXMEs in code

### Priority 5: Backlog 📚
- Planned features (if configured)
- Technical debt items

### Priority 6: AI Suggestions 💡
- Recommended next actions based on project state
- Effort estimates
- Priority guidance

## Usage

### Standalone

```bash
python scripts/report.py
```

### From Claude Code

```
/project-report
```

### Programmatic

```python
from report import ReportGenerator

generator = ReportGenerator()
report = generator.generate()
print(report)
```

## Output Format

Markdown report with sections in priority order. Designed for quick scanning with emojis and clear hierarchy.

## Integration

**Used by session-management**: Automatically invoked during `/session-start` to provide onboarding context.

**Standalone utility**: Can be run independently without session management.

## Configuration

No configuration required. Automatically detects:
- Git repository
- Test frameworks (pytest)
- Session state (`.sessions/` directory)
- CCMP plugin state (`.ccmp/state.json`)

## Best Practices

**Quick check**: Run `/project-report` anytime you need project overview

**Before work**: Check health indicators before starting new work

**After context switch**: First command after returning to project

**Share with team**: Generate report for handoffs or status updates

## See Also

- **session-management**: Uses this skill for session start onboarding
- **claude-context-manager**: Provides context health metrics
```

**Step 2: Commit SKILL.md**

```bash
git add plugins/project-status-report/skills/project-status-report/SKILL.md
git commit -m "docs(project-status-report): add SKILL.md documentation"
```

### Task 7: Slash Command Integration

**Files:**
- Create: `plugins/project-status-report/commands/project-report.md`

**Step 1: Write slash command**

Create `plugins/project-status-report/commands/project-report.md`:

```markdown
---
description: Generate comprehensive project status and health report
---

Execute the project-status-report skill to generate a comprehensive health report.

Run the report generator and display the full project status including:
- Health indicators (tests, linting, coverage)
- Git status (branch, commits, sync)
- Recent session summary
- Open work items (objectives, TODOs, FIXMEs)
- Suggested next actions

Use this command anytime you need project overview or are starting work after context switch.
```

**Step 2: Commit slash command**

```bash
git add plugins/project-status-report/commands/project-report.md
git commit -m "feat(project-status-report): add /project-report slash command"
```

---

## Phase 2: Session Management Refactor

### Task 8: Checkpoint Module

**Files:**
- Create: `plugins/session-management/skills/session-management/scripts/checkpoint.py`
- Create: `plugins/session-management/skills/session-management/scripts/test_checkpoint.py`

**Step 1: Write test for checkpoint generation**

Create `plugins/session-management/skills/session-management/scripts/test_checkpoint.py`:

```python
import pytest
from pathlib import Path
from checkpoint import CheckpointManager

def test_analyze_git_changes():
    """Test analyzing git diff for changes"""
    manager = CheckpointManager()
    changes = manager.analyze_git_changes()
    assert isinstance(changes, dict)
    assert "modified" in changes
    assert "added" in changes
    assert "deleted" in changes

def test_generate_checkpoint():
    """Test generating checkpoint document"""
    manager = CheckpointManager()
    checkpoint = manager.generate_checkpoint(notes="Test notes")
    assert isinstance(checkpoint, str)
    assert "Checkpoint:" in checkpoint
    assert "What Changed" in checkpoint
```

**Step 2: Run tests to verify they fail**

Run: `cd plugins/session-management/skills/session-management/scripts && pytest test_checkpoint.py -v`
Expected: FAIL with "No module named 'checkpoint'"

**Step 3: Write CheckpointManager implementation**

Create `plugins/session-management/skills/session-management/scripts/checkpoint.py`:

```python
#!/usr/bin/env python3
"""
Checkpoint Manager

Handles automatic checkpoint generation with git diff analysis.
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class CheckpointManager:
    """Manage session checkpoints"""

    def __init__(self, project_path: str = "."):
        """Initialize manager with project path"""
        self.project_path = Path(project_path)
        self.checkpoints_dir = self.project_path / ".sessions" / "checkpoints"
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)

    def _run_git(self, args: List[str]) -> Optional[str]:
        """Run git command"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def analyze_git_changes(self) -> Dict[str, List[str]]:
        """Analyze git diff for file changes"""
        # Get modified files with stats
        diff_output = self._run_git(["diff", "--stat"])

        modified = []
        added = []
        deleted = []

        if diff_output:
            for line in diff_output.split("\n"):
                if "|" in line:
                    filename = line.split("|")[0].strip()
                    modified.append(filename)

        # Get staged files
        staged_output = self._run_git(["diff", "--cached", "--name-status"])
        if staged_output:
            for line in staged_output.split("\n"):
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) == 2:
                    status, filename = parts
                    if status == "A":
                        added.append(filename)
                    elif status == "D":
                        deleted.append(filename)
                    elif status == "M":
                        if filename not in modified:
                            modified.append(filename)

        return {
            "modified": modified,
            "added": added,
            "deleted": deleted
        }

    def get_recent_commits(self, since_checkpoint: Optional[str] = None) -> List[str]:
        """Get commits since last checkpoint"""
        if since_checkpoint:
            # TODO: Track checkpoint commits
            pass

        # Get last 5 commits
        log_output = self._run_git(["log", "--oneline", "-5"])
        if log_output:
            return log_output.split("\n")
        return []

    def load_tdd_metrics(self) -> Optional[Dict]:
        """Load TDD metrics from .ccmp/state.json"""
        state_file = self.project_path / ".ccmp" / "state.json"

        if not state_file.exists():
            return None

        try:
            with open(state_file) as f:
                state = json.load(f)

            tdd_state = state.get("tdd-workflow", {})
            if tdd_state.get("active"):
                return {
                    "cycles_today": tdd_state.get("cycles_today", 0),
                    "current_phase": tdd_state.get("current_phase", "N/A"),
                    "discipline_score": tdd_state.get("discipline_score", 100)
                }
        except (json.JSONDecodeError, IOError):
            pass

        return None

    def generate_checkpoint(self, notes: Optional[str] = None, label: Optional[str] = None) -> str:
        """Generate checkpoint document"""
        timestamp = datetime.now()
        checkpoint_id = timestamp.strftime("%Y-%m-%dT%H-%M-%S")

        changes = self.analyze_git_changes()
        commits = self.get_recent_commits()
        tdd_metrics = self.load_tdd_metrics()

        lines = []
        lines.append(f"# Checkpoint: {checkpoint_id}")
        if label:
            lines.append(f"**Label**: {label}")
        lines.append(f"**Time**: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # What Changed
        lines.append("## What Changed")
        lines.append("")
        if changes["modified"]:
            lines.append("**Modified**:")
            for file in changes["modified"][:10]:
                lines.append(f"- {file}")
        if changes["added"]:
            lines.append("**Added**:")
            for file in changes["added"][:10]:
                lines.append(f"- {file}")
        if changes["deleted"]:
            lines.append("**Deleted**:")
            for file in changes["deleted"][:10]:
                lines.append(f"- {file}")

        if not any([changes["modified"], changes["added"], changes["deleted"]]):
            lines.append("*No changes detected*")

        lines.append("")

        # Commits
        if commits:
            lines.append("## Commits Since Last Checkpoint")
            lines.append("")
            for commit in commits:
                lines.append(f"- {commit}")
            lines.append("")

        # TDD Metrics
        if tdd_metrics:
            lines.append("## TDD Metrics")
            lines.append("")
            lines.append(f"- Cycles today: {tdd_metrics['cycles_today']}")
            lines.append(f"- Current phase: {tdd_metrics['current_phase']}")
            lines.append(f"- Discipline score: {tdd_metrics['discipline_score']}/100")
            lines.append("")

        # Notes
        if notes:
            lines.append("## Notes")
            lines.append("")
            lines.append(notes)
            lines.append("")

        checkpoint_content = "\n".join(lines)

        # Save checkpoint
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.md"
        with open(checkpoint_file, 'w') as f:
            f.write(checkpoint_content)

        return checkpoint_content

    def get_latest_checkpoint(self) -> Optional[Path]:
        """Get most recent checkpoint file"""
        checkpoints = sorted(self.checkpoints_dir.glob("*.md"), reverse=True)
        return checkpoints[0] if checkpoints else None


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Create session checkpoint")
    parser.add_argument("--label", help="Checkpoint label")
    parser.add_argument("--notes", help="Checkpoint notes")

    args = parser.parse_args()

    manager = CheckpointManager()
    checkpoint = manager.generate_checkpoint(notes=args.notes, label=args.label)
    print(checkpoint)
    print(f"\nCheckpoint saved to .sessions/checkpoints/")


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to verify they pass**

Run: `cd plugins/session-management/skills/session-management/scripts && pytest test_checkpoint.py -v`
Expected: PASS

**Step 5: Commit checkpoint module**

```bash
git add plugins/session-management/skills/session-management/scripts/checkpoint.py
git add plugins/session-management/skills/session-management/scripts/test_checkpoint.py
git commit -m "feat(session-management): add checkpoint manager with automatic git analysis"
```

### Task 9: Handoff Generator

**Files:**
- Create: `plugins/session-management/skills/session-management/scripts/handoff.py`
- Create: `plugins/session-management/skills/session-management/scripts/test_handoff.py`

**Step 1: Write test for handoff generation**

Create `plugins/session-management/skills/session-management/scripts/test_handoff.py`:

```python
import pytest
from handoff import HandoffGenerator

def test_generate_handoff():
    """Test generating session handoff document"""
    generator = HandoffGenerator()
    handoff = generator.generate_handoff(
        session_notes="Test session notes"
    )
    assert isinstance(handoff, str)
    assert "Session Handoff" in handoff
    assert "Test session notes" in handoff
```

**Step 2: Run tests to verify they fail**

Run: `cd plugins/session-management/skills/session-management/scripts && pytest test_handoff.py -v`
Expected: FAIL with "No module named 'handoff'"

**Step 3: Write HandoffGenerator implementation**

Create `plugins/session-management/skills/session-management/scripts/handoff.py`:

```python
#!/usr/bin/env python3
"""
Handoff Generator

Generates comprehensive session handoff documents.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

from checkpoint import CheckpointManager


class HandoffGenerator:
    """Generate session handoff documents"""

    def __init__(self, project_path: str = "."):
        """Initialize generator"""
        self.project_path = Path(project_path)
        self.checkpoint_manager = CheckpointManager(project_path)

    def load_session_state(self) -> Dict:
        """Load current session state"""
        state_file = self.project_path / ".sessions" / "state.json"

        if state_file.exists():
            try:
                with open(state_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        return {}

    def generate_handoff(self, session_notes: str) -> str:
        """Generate comprehensive handoff document"""
        timestamp = datetime.now()
        handoff_id = timestamp.strftime("%Y-%m-%dT%H-%M-%S") + "-HANDOFF"

        state = self.load_session_state()
        changes = self.checkpoint_manager.analyze_git_changes()

        lines = []
        lines.append(f"# Session Handoff: {timestamp.strftime('%Y-%m-%d')}")
        lines.append("")
        lines.append(f"**Branch**: {state.get('branch', 'Unknown')}")
        lines.append(f"**Date**: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Session Summary
        lines.append("## Session Summary")
        lines.append("")
        lines.append(session_notes)
        lines.append("")

        # What Changed
        lines.append("## What Changed (This Session)")
        lines.append("")

        total_modified = len(changes["modified"])
        total_added = len(changes["added"])
        total_deleted = len(changes["deleted"])

        lines.append(f"**Files modified**: {total_modified}")
        lines.append(f"**Files added**: {total_added}")
        lines.append(f"**Files deleted**: {total_deleted}")
        lines.append("")

        if changes["modified"]:
            lines.append("### Modified Files")
            for file in changes["modified"][:10]:
                lines.append(f"- {file}")
            if len(changes["modified"]) > 10:
                lines.append(f"- ... and {len(changes['modified']) - 10} more")
            lines.append("")

        # Open Work
        lines.append("## What's Next (Open Work)")
        lines.append("")

        objectives = state.get("objectives", [])
        if objectives:
            lines.append("**Objectives**:")
            for obj in objectives:
                if isinstance(obj, dict):
                    status = "[x]" if obj.get("completed") else "[ ]"
                    lines.append(f"- {status} {obj.get('text')}")
                else:
                    lines.append(f"- [ ] {obj}")
            lines.append("")

        # Context Health
        lines.append("## Context Health")
        lines.append("")
        lines.append("✅ Session state saved")
        lines.append("")

        # Next Steps (AI Suggestions placeholder)
        lines.append("## Next Steps (Suggested)")
        lines.append("")
        lines.append("1. Review changes since last session")
        lines.append("2. Continue work on open objectives")
        lines.append("")

        handoff_content = "\n".join(lines)

        # Save handoff
        handoff_file = self.checkpoint_manager.checkpoints_dir / f"{handoff_id}.md"
        with open(handoff_file, 'w') as f:
            f.write(handoff_content)

        return handoff_content


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate session handoff")
    parser.add_argument("--notes", required=True, help="Session summary notes")

    args = parser.parse_args()

    generator = HandoffGenerator()
    handoff = generator.generate_handoff(session_notes=args.notes)
    print(handoff)
    print(f"\nHandoff saved to .sessions/checkpoints/")


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to verify they pass**

Run: `cd plugins/session-management/skills/session-management/scripts && pytest test_handoff.py -v`
Expected: PASS

**Step 5: Commit handoff generator**

```bash
git add plugins/session-management/skills/session-management/scripts/handoff.py
git add plugins/session-management/skills/session-management/scripts/test_handoff.py
git commit -m "feat(session-management): add handoff generator for session end"
```

### Task 10: Update Session CLI

**Files:**
- Modify: `plugins/session-management/skills/session-management/scripts/session.py`

**Step 1: Read existing session.py**

Run: `cat plugins/session-management/skills/session-management/scripts/session.py | head -50`
Expected: View current implementation

**Step 2: Refactor checkpoint command to use CheckpointManager**

In `plugins/session-management/skills/session-management/scripts/session.py`, update the `cmd_checkpoint` function:

```python
def cmd_checkpoint(args):
    """Create checkpoint"""
    if not check_session_initialized():
        return 1

    # Use new CheckpointManager
    from checkpoint import CheckpointManager

    manager = CheckpointManager()
    checkpoint = manager.generate_checkpoint(
        notes=args.notes,
        label=args.label
    )

    print(checkpoint)
    print(f"\n✅ Checkpoint saved")

    # Git commit handling (if requested)
    if args.commit:
        # Check for uncommitted changes
        try:
            result = subprocess.run(
                ["git", "diff", "--quiet"],
                capture_output=True
            )
            if result.returncode != 0:  # There are changes
                response = input("Stage and commit changes? [Y/n]: ")
                if response.lower() != 'n':
                    # Stage all changes
                    subprocess.run(["git", "add", "."], check=True)
                    # Create commit
                    commit_msg = args.message or f"checkpoint: {args.label or 'progress'}"
                    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                    print("📝 Git commit created")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git commit failed: {e}")

    return 0
```

**Step 3: Refactor end command to use HandoffGenerator**

In `plugins/session-management/skills/session-management/scripts/session.py`, update the `cmd_end` function:

```python
def cmd_end(args):
    """End session"""
    if not check_session_initialized():
        return 1

    # Prompt for session notes
    print("\nSession Summary Notes:")
    print("\nWhat did you accomplish?")
    accomplished = input("> ")
    print("\nKey decisions made?")
    decisions = input("> ")
    print("\nWhat to remember for next session?")
    remember = input("> ")

    session_notes = f"""**Accomplished**: {accomplished}

**Decisions**: {decisions}

**Remember**: {remember}
"""

    # Generate handoff
    from handoff import HandoffGenerator

    generator = HandoffGenerator()
    handoff = generator.generate_handoff(session_notes=session_notes)

    print("\n" + handoff)
    print(f"\n✅ Session ended. Handoff generated.")

    # Git push handling
    if args.push:
        try:
            # Check for commits to push
            result = subprocess.run(
                ["git", "log", "@{u}..", "--oneline"],
                capture_output=True,
                text=True,
                check=True
            )
            commits = result.stdout.strip().split("\n")

            if commits and commits[0]:
                print(f"\nCommits to push: {len(commits)}")
                for commit in commits[:5]:
                    print(f"  - {commit}")

                response = input(f"\nPush {len(commits)} commits to remote? [Y/n]: ")
                if response.lower() != 'n':
                    subprocess.run(["git", "push"], check=True)
                    print("📤 Pushed to remote")
        except subprocess.CalledProcessError:
            print("⚠️  No commits to push or git push failed")

    return 0
```

**Step 4: Add --commit and --push flags to argument parsers**

In the `main()` function, update checkpoint parser:

```python
# checkpoint command
checkpoint_parser = subparsers.add_parser("checkpoint", help="Create checkpoint")
checkpoint_parser.add_argument("--label", help="Checkpoint label")
checkpoint_parser.add_argument("--notes", help="Checkpoint notes")
checkpoint_parser.add_argument("--commit", action="store_true", help="Create git commit")
checkpoint_parser.add_argument("--message", help="Commit message")
checkpoint_parser.set_defaults(func=cmd_checkpoint)
```

Update end parser:

```python
# end command
end_parser = subparsers.add_parser("end", help="End session")
end_parser.add_argument("--push", action="store_true", default=True, help="Push commits to remote")
end_parser.set_defaults(func=cmd_end)
```

**Step 5: Test checkpoint command**

Run: `cd plugins/session-management/skills/session-management/scripts && python session.py checkpoint --label "test" --notes "Test checkpoint"`
Expected: Creates checkpoint in .sessions/checkpoints/

**Step 6: Commit session.py refactor**

```bash
git add plugins/session-management/skills/session-management/scripts/session.py
git commit -m "refactor(session-management): integrate checkpoint and handoff generators into CLI"
```

### Task 11: Session Start Integration

**Files:**
- Modify: `plugins/session-management/skills/session-management/scripts/session.py`

**Step 1: Add project-status-report integration to session start**

Update `cmd_start` function in `session.py`:

```python
def cmd_start(args):
    """Start new session"""
    if not check_session_initialized():
        return 1

    # Generate project status report
    print("📊 Generating project status report...\n")

    # Import from project-status-report plugin
    import sys
    from pathlib import Path

    # Add project-status-report to path
    report_plugin_path = Path(__file__).parents[5] / "plugins" / "project-status-report" / "skills" / "project-status-report" / "scripts"
    sys.path.insert(0, str(report_plugin_path))

    try:
        from report import ReportGenerator

        generator = ReportGenerator()
        report = generator.generate()
        print(report)
        print("\n" + "=" * 60 + "\n")
    except ImportError:
        print("⚠️  project-status-report plugin not found, skipping report\n")

    # Present options (simplified for now)
    print("What would you like to work on?")
    print()
    print("1. Resume existing work (if available)")
    print("2. Start new work")
    print("3. Address health issues first")
    print()

    choice = input("Choice [1/2/3]: ")

    # Handle branch selection based on choice
    branch = args.branch
    if not branch:
        if choice == "1":
            # TODO: Load branch from last session
            branch = input("Enter branch name to resume: ")
        else:
            branch = input("Enter new branch name: ")

    # Checkout or create branch
    try:
        subprocess.run(["git", "checkout", branch], check=True, capture_output=True)
        print(f"✅ Switched to branch: {branch}")
    except subprocess.CalledProcessError:
        # Branch doesn't exist, create it
        try:
            subprocess.run(["git", "checkout", "-b", branch], check=True, capture_output=True)
            print(f"✅ Created new branch: {branch}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create branch: {e}")
            return 1

    # Parse objectives
    objectives = []
    if args.objective:
        objectives = [obj.strip() for obj in args.objective.split(',')]
    else:
        print("\nEnter session objectives (comma-separated):")
        obj_input = input("> ")
        if obj_input:
            objectives = [obj.strip() for obj in obj_input.split(',')]

    # Save session state
    state = {
        "branch": branch,
        "objectives": objectives,
        "started_at": datetime.now().isoformat(),
        "mode": "tdd" if args.tdd else "normal"
    }

    state_file = Path(".sessions") / "state.json"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Update .ccmp/state.json if available
    ccmp_state_file = Path(".ccmp") / "state.json"
    if ccmp_state_file.parent.exists():
        try:
            if ccmp_state_file.exists():
                with open(ccmp_state_file) as f:
                    ccmp_state = json.load(f)
            else:
                ccmp_state = {}

            ccmp_state["session-management"] = {
                "active": True,
                "branch": branch,
                "objectives": objectives,
                "mode": state["mode"]
            }

            with open(ccmp_state_file, 'w') as f:
                json.dump(ccmp_state, f, indent=2)
        except (json.JSONDecodeError, IOError):
            pass

    # Display session ready message
    print("\n" + "=" * 60)
    print("🚀 SESSION READY")
    print("=" * 60)
    print(f"Branch: {branch}")
    print(f"Mode: {state['mode'].upper()}")
    if objectives:
        print("\n📋 OBJECTIVES:")
        for i, obj in enumerate(objectives, 1):
            print(f"  {i}. {obj}")
    print("=" * 60)

    return 0
```

**Step 2: Add necessary imports at top of file**

```python
import json
from datetime import datetime
```

**Step 3: Test session start**

Run: `cd plugins/session-management/skills/session-management/scripts && python session.py start test-branch --objective "Test objective"`
Expected: Shows project report, creates session, saves state

**Step 4: Commit session start integration**

```bash
git add plugins/session-management/skills/session-management/scripts/session.py
git commit -m "feat(session-management): integrate project-status-report into session start"
```

### Task 12: Slash Commands

**Files:**
- Create: `plugins/session-management/commands/session-start.md`
- Create: `plugins/session-management/commands/checkpoint.md`
- Create: `plugins/session-management/commands/session-end.md`

**Step 1: Create /session-start command**

Create `plugins/session-management/commands/session-start.md`:

```markdown
---
description: Start or resume coding session with AI-guided context loading
---

Execute session-management skill's start workflow.

This will:
1. Generate comprehensive project status report
2. Present context-aware options for what to work on
3. Guide branch selection with best practices
4. Load full project context (architecture, decisions, patterns)
5. Set up session state and objectives

Use this command when:
- Starting work on a project
- Returning after context switch
- Beginning a new feature or fix
```

**Step 2: Create /checkpoint command**

Create `plugins/session-management/commands/checkpoint.md`:

```markdown
---
description: Create session checkpoint with automatic state capture
---

Execute session-management skill's checkpoint workflow.

This will:
1. Automatically analyze git changes
2. Capture metrics (TDD cycles, test coverage, etc.)
3. Optionally prompt for checkpoint notes
4. Generate checkpoint document
5. Optionally create git commit

Use this command:
- At logical milestones during work
- Before switching contexts
- When completing a sub-task
```

**Step 3: Create /session-end command**

Create `plugins/session-management/commands/session-end.md`:

```markdown
---
description: End session with comprehensive handoff generation
---

Execute session-management skill's finish workflow.

This will:
1. Create final checkpoint
2. Prompt for session summary notes
3. Generate comprehensive handoff document
4. Handle git push with confirmation
5. Save session state for next time

Use this command:
- When finishing work on a project
- End of day or before context switch
- After completing feature/fix
```

**Step 4: Commit slash commands**

```bash
git add plugins/session-management/commands/
git commit -m "feat(session-management): add slash commands for session lifecycle"
```

### Task 13: Update SKILL.md

**Files:**
- Modify: `plugins/session-management/skills/session-management/SKILL.md`

**Step 1: Update SKILL.md with new workflows**

Update the workflow sections in SKILL.md to reflect the refactored implementation:

```markdown
## Core Workflows

### Session Start (`/session-start`)

**Rapid re-immersion for both human and AI**

```bash
/session-start
```

**What happens:**
1. **Project status report generated** - Health, git status, recent work, open items
2. **Context-aware options presented** - AI-guided suggestions based on project state
3. **Branch selection** - Best practice guidance for branch management
4. **Context loaded** - Architecture, decisions, patterns from last session
5. **Session ready** - Both human and AI fully contextualized

**Use when:**
- Starting work on a project
- Returning after days away
- Context switching between projects

### Create Checkpoint (`/checkpoint`)

**Quick save points during work**

```bash
/checkpoint
```

**What happens:**
1. **Automatic capture** - Git diff, metrics, TDD cycles analyzed
2. **Optional notes** - Add context if desired (press Enter to skip)
3. **Checkpoint saved** - Comprehensive snapshot generated
4. **Git commit** - Optionally create commit

**Use when:**
- At logical milestones
- Completing sub-tasks
- Before switching contexts

### End Session (`/session-end`)

**Comprehensive knowledge capture and handoff**

```bash
/session-end
```

**What happens:**
1. **Session notes prompt** - Capture what you accomplished, decisions, what to remember
2. **Handoff generated** - Full session summary with next steps
3. **Git push** - Optionally push commits to remote
4. **State saved** - Ready for next session

**Use when:**
- Finishing work session
- End of day
- Before extended break
```

**Step 2: Commit SKILL.md update**

```bash
git add plugins/session-management/skills/session-management/SKILL.md
git commit -m "docs(session-management): update SKILL.md with refactored workflows"
```

---

## Phase 3: Integration & Testing

### Task 14: Integration Testing

**Files:**
- Create: `docs/plans/2025-11-04-integration-test-results.md`

**Step 1: Test full workflow manually**

1. Initialize session in test project:
```bash
cd /tmp/test-project
python /path/to/plugins/session-management/skills/session-management/scripts/init_session.py
```

2. Start session:
```bash
python /path/to/plugins/session-management/skills/session-management/scripts/session.py start test-feature --objective "Test feature"
```

Expected: Shows project report, creates session

3. Make some changes, create checkpoint:
```bash
echo "# Test" > test.md
python /path/to/plugins/session-management/skills/session-management/scripts/session.py checkpoint --label "test checkpoint" --commit
```

Expected: Creates checkpoint and git commit

4. End session:
```bash
python /path/to/plugins/session-management/skills/session-management/scripts/session.py end
```

Expected: Prompts for notes, generates handoff

**Step 2: Document test results**

Create `docs/plans/2025-11-04-integration-test-results.md` with findings

**Step 3: Fix any issues found during testing**

Address bugs and commit fixes

**Step 4: Commit test results**

```bash
git add docs/plans/2025-11-04-integration-test-results.md
git commit -m "test: document integration test results for session management refactor"
```

### Task 15: Final Documentation

**Files:**
- Create: `docs/guides/session-management-quickstart.md`
- Update: `README.md` (if exists in plugins)

**Step 1: Create quickstart guide**

Create `docs/guides/session-management-quickstart.md`:

```markdown
# Session Management Quick Start

Get started with git-native session management in 5 minutes.

## Installation

Install the plugins:

```bash
claude plugin install project-status-report
claude plugin install session-management
```

## Initialize in Your Project

```bash
cd your-project
python -c "from session_management import init_session; init_session.main()"
```

This creates `.sessions/` directory structure.

## Your First Session

### 1. Start Session

```bash
/session-start
```

You'll see:
- Project health report
- Git status
- Options for what to work on

Choose an option, select/create branch, set objectives.

### 2. Do Work

Work normally using your superpowers skills (TDD, debugging, etc.).

Session management observes in the background.

### 3. Create Checkpoints

```bash
/checkpoint
```

Quick save point. Optionally add notes or create git commit.

### 4. End Session

```bash
/session-end
```

Answer prompts for session summary. Handoff document generated.

## Next Session

```bash
/session-start
```

Your previous handoff is loaded automatically. Pick up where you left off.

## Key Commands

- `/project-report` - Check project status anytime
- `/session-start` - Start/resume session
- `/checkpoint` - Quick save during work
- `/session-end` - Finish with handoff

## Best Practices

1. **Start every session** - Get full context, make informed decisions
2. **Checkpoint at milestones** - Logical save points, not after every change
3. **End with good notes** - Future you will thank current you
4. **Use project-report mid-session** - Quick health check without overhead

## Troubleshooting

**Session not starting?**
- Ensure `.sessions/` directory exists
- Run init_session.py first

**Report not showing?**
- project-status-report plugin must be installed
- Falls back gracefully if not available

**Git operations failing?**
- Ensure you're in a git repository
- Check remote is configured for push operations
```

**Step 2: Commit documentation**

```bash
git add docs/guides/session-management-quickstart.md
git commit -m "docs: add session management quick start guide"
```

### Task 16: Final Commit and Summary

**Step 1: Run all tests**

```bash
cd plugins/project-status-report/skills/project-status-report/scripts
pytest -v

cd plugins/session-management/skills/session-management/scripts
pytest -v
```

Expected: All tests passing

**Step 2: Validate plugins**

```bash
claude plugin validate plugins/project-status-report
claude plugin validate plugins/session-management
```

Expected: Validation passes

**Step 3: Create final summary commit**

```bash
git commit --allow-empty -m "feat: complete session-management refactoring

Implemented git-native session onboarding system with two-skill architecture.

**Phase 1: Project Status Report (NEW)**
- Health check module (tests, linting, coverage, context)
- Git analysis module (branches, sync status, changes)
- Work items scanner (TODOs, FIXMEs, objectives)
- Report generator CLI
- /project-report slash command

**Phase 2: Session Management (REFACTORED)**
- CheckpointManager with automatic git diff analysis
- HandoffGenerator for comprehensive session end
- Refactored session CLI (start, checkpoint, end)
- Integration with project-status-report
- Slash commands: /session-start, /checkpoint, /session-end

**Phase 3: Integration**
- Observer pattern for superpowers (TDD, verification)
- .ccmp/state.json coordination
- Project-local storage (.sessions/)
- Full test coverage

**Success Criteria Met:**
✅ Session start < 2 minutes with full context
✅ Automatic checkpoint capture (no required input)
✅ Comprehensive handoff generation
✅ Git best practices automated with confirmations
✅ Standalone skills (works without other plugins)

Ready for deployment and user testing.
"
```

---

## Execution Handoff

Plan complete and saved to `docs/plans/2025-11-04-session-management-implementation.md`.

**Two execution options:**

**1. Subagent-Driven (this session)**
- I dispatch fresh subagent per task
- Code review between tasks
- Fast iteration in current session
- **REQUIRED SUB-SKILL:** superpowers:subagent-driven-development

**2. Parallel Session (separate)**
- Open new session in worktree
- Batch execution with checkpoints
- **REQUIRED SUB-SKILL:** superpowers:executing-plans

**Which approach would you like?**
