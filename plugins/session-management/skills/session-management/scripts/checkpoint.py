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
