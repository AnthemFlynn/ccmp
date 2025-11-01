#!/usr/bin/env python3
"""
Session Integration Helpers

Functions to integrate session-management with context-manager and tdd-workflow.
"""

import sys
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ccmp_integration import CCMPIntegration, get_context_health
from context_loader import ContextLoader
from test_pattern_analyzer import TestPatternAnalyzer


class SessionIntegration:
    """Integration helpers for session-management."""

    def __init__(self, repo_path: Optional[str] = None):
        """Initialize session integration."""
        self.integration = CCMPIntegration(repo_path)
        self.context_loader = ContextLoader(repo_path)
        self.pattern_analyzer = TestPatternAnalyzer()
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()

    def start_session(self, branch: str, objectives: List[str], mode: str = "normal"):
        """
        Start a session with full integration.

        Args:
            branch: Branch name
            objectives: List of session objectives
            mode: Session mode ("normal" or "tdd")

        Returns:
            Brief string for agent onboarding
        """
        # Update integration state
        self.integration.update_state("session-management", {
            "active": True,
            "current_session": branch,
            "branch": branch,
            "mode": mode,
            "objectives": objectives
        })

        # Generate comprehensive brief
        brief_parts = [
            "🚀 SESSION STARTED",
            "=" * 60,
            f"Branch: {branch}",
            f"Mode: {mode.upper()}",
            "",
            "📋 OBJECTIVES:",
        ]

        for i, obj in enumerate(objectives, 1):
            brief_parts.append(f"  {i}. {obj}")

        brief_parts.append("")

        # Load relevant context
        context_brief = self.context_loader.generate_context_brief(objectives)
        brief_parts.append(context_brief)

        # Check context health
        health = get_context_health()
        if health and health.get("health_score") is not None:
            score = health["health_score"]
            brief_parts.append("🏥 CONTEXT HEALTH")
            brief_parts.append(f"   Overall: {score}/100")

            if health.get("critical_files"):
                brief_parts.append(f"   ⚠️  {len(health['critical_files'])} files need attention")

        # TDD mode notice
        if mode == "tdd":
            brief_parts.append("")
            brief_parts.append("🧪 TDD MODE ACTIVE")
            brief_parts.append("   • RED-GREEN-REFACTOR cycle enforcement")
            brief_parts.append("   • Automatic phase checkpoints")
            brief_parts.append("   • Test metrics tracking")

        brief_parts.append("")
        brief_parts.append("=" * 60)
        brief_parts.append("Ready to code! 💻")
        brief_parts.append("")

        return "\n".join(brief_parts)

    def checkpoint(self, label: str, changed_directories: Optional[List[Path]] = None) -> str:
        """
        Create checkpoint with context health check.

        Args:
            label: Checkpoint label
            changed_directories: Directories that changed (for context health check)

        Returns:
            Status message
        """
        messages = [f"✅ Checkpoint created: {label}"]

        # Check context health for changed directories
        if changed_directories:
            health_report = self.context_loader.check_context_health(changed_directories)

            if health_report["stale"]:
                messages.append("")
                messages.append("⚠️  CONTEXT HEALTH WARNING:")
                for item in health_report["stale"]:
                    messages.append(f"   • {item['path']} (stale: {item['age_days']} days)")
                messages.append("")
                messages.append("💡 Update context? Run: python scripts/auto_update.py <directory>")

            if health_report["missing"]:
                messages.append("")
                messages.append("ℹ️  Missing context files:")
                for path in health_report["missing"]:
                    messages.append(f"   • {path}/")

        return "\n".join(messages)

    def end_session(self, generate_handoff: bool = True) -> str:
        """
        End session and generate handoff.

        Args:
            generate_handoff: Whether to generate full handoff document

        Returns:
            Handoff or completion message
        """
        # Get current session state
        session_state = self.integration.get_state("session-management")

        # Deactivate session
        self.integration.update_state("session-management", {
            "active": False,
            "current_session": None
        })

        if not generate_handoff:
            return "Session ended."

        # Generate handoff
        handoff_parts = [
            "📝 SESSION HANDOFF",
            "=" * 60,
            f"Branch: {session_state.get('branch', 'unknown')}",
            f"Mode: {session_state.get('mode', 'normal').upper()}",
            ""
        ]

        # Check context health for handoff
        health = get_context_health()
        if health:
            score = health.get("health_score", "unknown")
            handoff_parts.append("🏥 CONTEXT HEALTH")
            handoff_parts.append(f"   Final score: {score}/100")

            if health.get("critical_files"):
                handoff_parts.append("   ⚠️  Attention needed:")
                for file in health["critical_files"][:5]:
                    handoff_parts.append(f"      • {file}")

            handoff_parts.append("")

        # TDD metrics (if TDD session)
        if session_state.get("mode") == "tdd":
            tdd_state = self.integration.get_state("tdd-workflow")
            handoff_parts.append("🧪 TDD METRICS")
            handoff_parts.append(f"   Cycles completed: {tdd_state.get('cycles_today', 0)}")
            handoff_parts.append(f"   Discipline score: {tdd_state.get('discipline_score', 100)}/100")

            # Add TDD analysis
            try:
                from tdd_analyzer import TDDAnalyzer
                analyzer = TDDAnalyzer(str(self.repo_path))
                commit_analysis = analyzer.analyze_session_commits()

                if commit_analysis["violations"]:
                    handoff_parts.append(f"   ⚠️  Violations detected: {sum(commit_analysis['violations'].values())}")

                handoff_parts.append(f"   Commits with tests: {commit_analysis['commits_with_tests']}")
                handoff_parts.append(f"   Commits without tests: {commit_analysis['commits_without_tests']}")
            except Exception:
                # If analysis fails, just skip it
                pass

            handoff_parts.append("")

        handoff_parts.append("=" * 60)
        handoff_parts.append("Session complete. Context preserved for next session.")
        handoff_parts.append("")

        return "\n".join(handoff_parts)

    def get_changed_test_files(self) -> List[Path]:
        """Get test files that have changed since last commit"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=True
            )

            files = result.stdout.strip().split('\n')
            test_files = []

            test_indicators = ['test_', '_test.', '.test.', '.spec.', '/tests/']

            for file in files:
                if file and any(indicator in file for indicator in test_indicators):
                    file_path = self.repo_path / file
                    if file_path.exists() and file_path.is_file():
                        test_files.append(file_path)

            return test_files
        except Exception:
            return []

    def update_test_context(self, test_files: List[Path]) -> Dict:
        """
        Analyze test files and update test context documentation.

        Args:
            test_files: List of test file paths

        Returns:
            Dict with update results
        """
        if not test_files:
            return {"updated": [], "patterns": {}}

        results = {
            "updated": [],
            "patterns": {},
            "errors": []
        }

        # Group test files by directory
        test_dirs = {}
        for test_file in test_files:
            test_dir = test_file.parent
            if test_dir not in test_dirs:
                test_dirs[test_dir] = []
            test_dirs[test_dir].append(test_file)

        # Analyze each directory's tests
        for test_dir, files in test_dirs.items():
            try:
                # Analyze all test files in this directory
                dir_analysis = self.pattern_analyzer.analyze_test_directory(test_dir)

                if "error" in dir_analysis:
                    results["errors"].append(f"{test_dir}: {dir_analysis['error']}")
                    continue

                # Generate context update
                context_file = test_dir / "claude.md"
                context_content = self._generate_test_context(test_dir, dir_analysis)

                # Update or create context file
                if context_file.exists():
                    # Update existing context
                    self._update_existing_test_context(context_file, dir_analysis)
                    results["updated"].append(str(context_file.relative_to(self.repo_path)))
                else:
                    # Create new context
                    context_file.write_text(context_content)
                    results["updated"].append(str(context_file.relative_to(self.repo_path)))

                results["patterns"][str(test_dir.relative_to(self.repo_path))] = dir_analysis.get("common_patterns", {})

            except Exception as e:
                results["errors"].append(f"{test_dir}: {str(e)}")

        return results

    def _generate_test_context(self, test_dir: Path, analysis: Dict) -> str:
        """Generate test context content from analysis"""
        lines = [
            f"# Test Directory: {test_dir.name}",
            "",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}",
            f"**Test Framework:** {', '.join(analysis.get('frameworks_detected', ['Unknown']))}",
            "",
            "## Overview",
            "",
            f"Contains {analysis.get('test_count', 0)} tests across {analysis.get('files_analyzed', 0)} files.",
            "",
            "## Test Patterns",
            ""
        ]

        # Add discovered patterns
        if analysis.get("common_patterns"):
            for pattern, count in sorted(analysis["common_patterns"].items(), key=lambda x: -x[1]):
                lines.append(f"- **{pattern}** (used in {count} files)")

        lines.append("")
        lines.append("## Test Structure")
        lines.append("")

        # Add file-specific information
        for file_name, file_analysis in analysis.get("files", {}).items():
            lines.append(f"### {file_name}")
            lines.append("")

            if file_analysis.get("test_functions"):
                lines.append(f"**Tests:** {len(file_analysis['test_functions'])}")

            if file_analysis.get("test_cases"):
                lines.append(f"**Test Cases:** {len(file_analysis['test_cases'])}")

            if file_analysis.get("fixtures"):
                lines.append(f"**Fixtures:** {', '.join(file_analysis['fixtures'])}")

            if file_analysis.get("patterns_found"):
                lines.append("")
                lines.append("**Patterns:**")
                for pattern in file_analysis["patterns_found"]:
                    lines.append(f"- {pattern}")

            lines.append("")

        lines.append("---")
        lines.append("*Auto-generated by TDD workflow integration*")

        return "\n".join(lines)

    def _update_existing_test_context(self, context_file: Path, analysis: Dict):
        """Update existing test context file with new patterns"""
        try:
            content = context_file.read_text()

            # Update last updated timestamp
            content = re.sub(
                r'\*\*Last Updated:\*\* \d{4}-\d{2}-\d{2}',
                f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}",
                content
            )

            # Update test count
            test_count = analysis.get('test_count', 0)
            content = re.sub(
                r'Contains \d+ tests',
                f"Contains {test_count} tests",
                content
            )

            context_file.write_text(content)
        except Exception:
            # If update fails, just log it
            pass

    def tdd_green_checkpoint(self, label: str, test_files: Optional[List[Path]] = None) -> str:
        """
        Handle GREEN checkpoint with automatic test context update.

        Args:
            label: Checkpoint label
            test_files: Optional list of test files (auto-detected if None)

        Returns:
            Status message
        """
        messages = [f"✅ GREEN Checkpoint: {label}"]

        # Get test files if not provided
        if test_files is None:
            test_files = self.get_changed_test_files()

        if test_files:
            messages.append(f"\n🧪 Analyzing {len(test_files)} test file(s)...")

            # Update test context
            update_results = self.update_test_context(test_files)

            if update_results["updated"]:
                messages.append("\n📝 Test context updated:")
                for updated in update_results["updated"]:
                    messages.append(f"   • {updated}")

            if update_results["patterns"]:
                messages.append("\n🔍 Patterns discovered:")
                for dir_path, patterns in update_results["patterns"].items():
                    if patterns:
                        top_pattern = max(patterns, key=patterns.get)
                        messages.append(f"   • {dir_path}: {top_pattern}")

            if update_results["errors"]:
                messages.append("\n⚠️  Some updates failed:")
                for error in update_results["errors"]:
                    messages.append(f"   • {error}")
        else:
            messages.append("\nℹ️  No test files changed")

        return "\n".join(messages)


def demo_integration():
    """Demonstrate the integration capabilities."""
    print("CCMP Session Integration Demo")
    print("=" * 60)
    print()

    # Create integration
    session_int = SessionIntegration()

    # Demo: Start session
    print("1. Starting TDD session...")
    print()
    brief = session_int.start_session(
        branch="feature/auth",
        objectives=["Implement OAuth2 authentication", "Add user session management"],
        mode="tdd"
    )
    print(brief)

    # Demo: Checkpoint
    print("\n2. Creating checkpoint after code changes...")
    print()
    # Note: In real usage, changed_directories would be detected from git
    # For demo, we'll skip directory checking
    checkpoint_msg = session_int.checkpoint(
        label="oauth-provider-complete",
        changed_directories=None  # Would be auto-detected in real usage
    )
    print(checkpoint_msg)

    # Demo: End session
    print("\n3. Ending session...")
    print()
    handoff = session_int.end_session(generate_handoff=True)
    print(handoff)


if __name__ == "__main__":
    demo_integration()
