#!/usr/bin/env python3
"""
TDD Violation Analyzer

Analyzes git history and sessions to detect TDD violations.

Usage:
    from tdd_analyzer import TDDAnalyzer

    analyzer = TDDAnalyzer()
    violations = analyzer.analyze_session("feature/auth")
"""

import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class TDDAnalyzer:
    """Analyzes sessions for TDD violations"""

    def __init__(self, repo_path: str = "."):
        """Initialize analyzer"""
        self.repo_path = Path(repo_path).resolve()

    def get_commits_since(self, since: str = "1 week ago") -> List[Dict]:
        """Get commits since a given time"""
        try:
            result = subprocess.run(
                ["git", "log", f"--since={since}", "--pretty=format:%H|%an|%ae|%s|%ad", "--date=iso"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=True
            )

            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "message": parts[3],
                        "date": parts[4]
                    })

            return commits
        except Exception:
            return []

    def get_commit_files(self, commit_hash: str) -> Dict[str, List[str]]:
        """Get files changed in a commit"""
        try:
            result = subprocess.run(
                ["git", "show", "--name-status", "--pretty=format:", commit_hash],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=True
            )

            files = {
                "test": [],
                "source": [],
                "other": []
            }

            test_indicators = ['test_', '_test.', '.test.', '.spec.', '/tests/', '/test/']

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = line.split('\t')
                if len(parts) >= 2:
                    file_path = parts[1]

                    if any(indicator in file_path for indicator in test_indicators):
                        files["test"].append(file_path)
                    elif file_path.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rb')):
                        files["source"].append(file_path)
                    else:
                        files["other"].append(file_path)

            return files
        except Exception:
            return {"test": [], "source": [], "other": []}

    def detect_commit_violations(self, commit: Dict) -> List[str]:
        """Detect TDD violations in a commit"""
        violations = []

        # Get files changed
        files = self.get_commit_files(commit["hash"])

        # Violation 1: Source code changes without test changes
        if files["source"] and not files["test"]:
            violations.append("source_without_tests")

        # Violation 2: Check commit message for TDD indicators
        message = commit["message"].lower()

        # Good signs
        if any(word in message for word in ["test", "tdd", "spec", "coverage"]):
            # Likely test-focused commit
            pass
        elif files["source"] and not files["test"]:
            # Source changes without test mention
            violations.append("no_test_mention")

        # Check for anti-patterns in message
        if any(phrase in message for phrase in ["fix test", "fix tests", "update test", "skip test"]):
            violations.append("test_fix_after_code")

        return violations

    def analyze_session_commits(self, branch: str = None) -> Dict:
        """Analyze commits in current session/branch"""
        if not branch:
            # Get current branch
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                    check=True
                )
                branch = result.stdout.strip()
            except Exception:
                branch = "main"

        # Get commits
        commits = self.get_commits_since("1 week ago")

        analysis = {
            "total_commits": len(commits),
            "violations": defaultdict(int),
            "clean_commits": 0,
            "commits_with_tests": 0,
            "commits_without_tests": 0,
            "tdd_score": 100,
            "recommendations": []
        }

        for commit in commits:
            violations = self.detect_commit_violations(commit)

            if not violations:
                analysis["clean_commits"] += 1

            files = self.get_commit_files(commit["hash"])

            if files["test"]:
                analysis["commits_with_tests"] += 1
            elif files["source"]:
                analysis["commits_without_tests"] += 1

            for violation in violations:
                analysis["violations"][violation] += 1

        # Calculate TDD score
        if analysis["total_commits"] > 0:
            violation_penalty = sum(analysis["violations"].values()) * 10
            analysis["tdd_score"] = max(0, 100 - violation_penalty)

        # Generate recommendations
        if analysis["commits_without_tests"] > 0:
            analysis["recommendations"].append(
                f"{analysis['commits_without_tests']} commits modified source without tests - ensure test-first development"
            )

        if analysis["violations"]["source_without_tests"] > 3:
            analysis["recommendations"].append(
                "High frequency of source changes without tests - review TDD discipline"
            )

        if analysis["violations"]["test_fix_after_code"] > 0:
            analysis["recommendations"].append(
                "Tests were fixed after implementation - tests should fail first"
            )

        # Convert defaultdict to dict
        analysis["violations"] = dict(analysis["violations"])

        return analysis

    def analyze_tdd_cycle_timing(self) -> Dict:
        """Analyze timing between test and implementation commits"""
        commits = self.get_commits_since("1 week ago")

        cycles = []
        current_cycle = {"red": None, "green": None}

        for commit in commits:
            message = commit["message"].lower()
            files = self.get_commit_files(commit["hash"])

            # Detect RED (test-only commit)
            if files["test"] and not files["source"]:
                if "red" in message or "fail" in message or "test" in message:
                    current_cycle["red"] = commit
                    current_cycle["red_time"] = datetime.fromisoformat(commit["date"].replace(' ', 'T').split('+')[0])

            # Detect GREEN (implementation commit)
            elif files["source"]:
                if current_cycle["red"]:
                    current_cycle["green"] = commit
                    current_cycle["green_time"] = datetime.fromisoformat(commit["date"].replace(' ', 'T').split('+')[0])

                    # Calculate cycle time
                    time_diff = current_cycle["green_time"] - current_cycle["red_time"]
                    current_cycle["duration_minutes"] = time_diff.total_seconds() / 60

                    cycles.append(current_cycle.copy())
                    current_cycle = {"red": None, "green": None}

        analysis = {
            "total_cycles": len(cycles),
            "average_cycle_time": 0,
            "fastest_cycle": None,
            "slowest_cycle": None
        }

        if cycles:
            durations = [c["duration_minutes"] for c in cycles]
            analysis["average_cycle_time"] = sum(durations) / len(durations)
            analysis["fastest_cycle"] = min(durations)
            analysis["slowest_cycle"] = max(durations)

        return analysis

    def generate_violation_report(self, analysis: Dict) -> str:
        """Generate human-readable violation report"""
        lines = [
            "🧪 TDD Analysis Report",
            "=" * 60,
            f"Total commits analyzed: {analysis['total_commits']}",
            f"TDD Score: {analysis['tdd_score']}/100",
            ""
        ]

        # Violations section
        if analysis["violations"]:
            lines.append("⚠️  Violations Detected:")
            for violation, count in analysis["violations"].items():
                violation_name = violation.replace('_', ' ').title()
                lines.append(f"  • {violation_name}: {count}")
            lines.append("")

        # Stats
        lines.append("📊 Statistics:")
        lines.append(f"  • Commits with tests: {analysis['commits_with_tests']}")
        lines.append(f"  • Commits without tests: {analysis['commits_without_tests']}")
        lines.append(f"  • Clean commits: {analysis['clean_commits']}")
        lines.append("")

        # Recommendations
        if analysis["recommendations"]:
            lines.append("💡 Recommendations:")
            for rec in analysis["recommendations"]:
                lines.append(f"  • {rec}")
            lines.append("")

        return "\n".join(lines)


def main():
    """CLI for TDD analyzer"""
    import sys

    analyzer = TDDAnalyzer()

    print("Analyzing TDD discipline...")
    print()

    # Analyze commits
    commit_analysis = analyzer.analyze_session_commits()
    print(analyzer.generate_violation_report(commit_analysis))

    # Analyze cycle timing
    cycle_analysis = analyzer.analyze_tdd_cycle_timing()
    if cycle_analysis["total_cycles"] > 0:
        print("⏱️  TDD Cycle Timing:")
        print(f"  • Total cycles: {cycle_analysis['total_cycles']}")
        print(f"  • Average cycle time: {cycle_analysis['average_cycle_time']:.1f} minutes")
        print(f"  • Fastest cycle: {cycle_analysis['fastest_cycle']:.1f} minutes")
        print(f"  • Slowest cycle: {cycle_analysis['slowest_cycle']:.1f} minutes")
        print()


if __name__ == "__main__":
    main()
