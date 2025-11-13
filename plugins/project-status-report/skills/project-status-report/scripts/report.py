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
