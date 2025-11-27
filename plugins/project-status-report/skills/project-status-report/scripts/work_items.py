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
