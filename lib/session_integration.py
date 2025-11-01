#!/usr/bin/env python3
"""
Session Integration Helpers

Functions to integrate session-management with context-manager and tdd-workflow.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ccmp_integration import CCMPIntegration, get_context_health
from context_loader import ContextLoader


class SessionIntegration:
    """Integration helpers for session-management."""

    def __init__(self, repo_path: Optional[str] = None):
        """Initialize session integration."""
        self.integration = CCMPIntegration(repo_path)
        self.context_loader = ContextLoader(repo_path)

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
            handoff_parts.append("")

        handoff_parts.append("=" * 60)
        handoff_parts.append("Session complete. Context preserved for next session.")
        handoff_parts.append("")

        return "\n".join(handoff_parts)


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
