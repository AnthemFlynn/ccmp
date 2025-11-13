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
