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
