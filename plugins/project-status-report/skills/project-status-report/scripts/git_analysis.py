#!/usr/bin/env python3
"""
Git Analysis Module

Analyzes git repository state for project status reports.
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


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
        # Get staged files
        staged_output = self._run_git(["diff", "--cached", "--name-only"])
        staged = staged_output.split("\n") if staged_output else []
        staged = [f for f in staged if f]  # Filter empty strings

        # Get modified files
        modified_output = self._run_git(["diff", "--name-only"])
        modified = modified_output.split("\n") if modified_output else []
        modified = [f for f in modified if f]  # Filter empty strings

        # Get untracked files
        untracked_output = self._run_git(["ls-files", "--others", "--exclude-standard"])
        untracked = untracked_output.split("\n") if untracked_output else []
        untracked = [f for f in untracked if f]

        return {
            "staged": staged,
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

    def get_remote_sync_status(self) -> Dict[str, Any]:
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
        if changes["staged"]:
            lines.append(f"**Staged**: {len(changes['staged'])} files")
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
