#!/usr/bin/env python3
"""
Context Loader for CCMP Integration

Loads relevant claude.md context files for sessions.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ContextLoader:
    """Load and parse claude.md context files."""

    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize context loader.

        Args:
            repo_path: Path to repository root. If None, uses current directory.
        """
        self.repo_path = Path(repo_path or os.getcwd()).resolve()

    def find_all_context_files(self) -> List[Path]:
        """
        Find all claude.md files in repository.

        Returns:
            List of paths to claude.md files
        """
        context_files = []
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden directories and common exclusions
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__']]

            if 'claude.md' in files:
                context_files.append(Path(root) / 'claude.md')

        return sorted(context_files)

    def find_relevant_context(self, objectives: List[str]) -> List[Path]:
        """
        Find context files relevant to session objectives.

        Args:
            objectives: List of session objective strings

        Returns:
            List of relevant claude.md file paths
        """
        all_contexts = self.find_all_context_files()

        if not objectives:
            return all_contexts

        # Extract keywords from objectives
        keywords = set()
        for obj in objectives:
            # Simple keyword extraction (lowercase, alphanumeric)
            words = re.findall(r'\b\w+\b', obj.lower())
            keywords.update(words)

        # Score each context file by directory name match
        scored = []
        for context_path in all_contexts:
            directory = context_path.parent.name.lower()
            relative_path = context_path.parent.relative_to(self.repo_path)

            # Score based on keyword matches in path
            score = 0
            path_str = str(relative_path).lower()
            for keyword in keywords:
                if keyword in path_str:
                    score += 1

            scored.append((score, context_path))

        # Sort by score (highest first) and return top matches
        scored.sort(reverse=True, key=lambda x: x[0])

        # Return files with score > 0, or all if no matches
        relevant = [path for score, path in scored if score > 0]
        return relevant if relevant else all_contexts[:5]  # Top 5 if no matches

    def read_context(self, context_path: Path) -> Dict[str, any]:
        """
        Read and parse a claude.md file.

        Args:
            context_path: Path to claude.md file

        Returns:
            Dictionary with parsed context data
        """
        try:
            with open(context_path, 'r') as f:
                content = f.read()

            return {
                "path": context_path,
                "relative_path": context_path.relative_to(self.repo_path),
                "directory": context_path.parent.name,
                "content": content,
                "summary": self._extract_summary(content),
                "patterns": self._extract_patterns(content),
                "gotchas": self._extract_gotchas(content)
            }
        except Exception as e:
            return {
                "path": context_path,
                "error": str(e)
            }

    def _extract_summary(self, content: str) -> str:
        """Extract purpose/summary from context."""
        # Look for purpose section
        purpose_match = re.search(r'##\s*Purpose\s*\n+(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if purpose_match:
            return purpose_match.group(1).strip()[:200]  # First 200 chars

        # Fallback: first paragraph
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('#'):
                return line.strip()[:200]

        return "No summary available"

    def _extract_patterns(self, content: str) -> List[str]:
        """Extract key patterns from context."""
        patterns = []

        # Look for patterns section
        pattern_match = re.search(r'##\s*Patterns?\s*\n+(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if pattern_match:
            pattern_text = pattern_match.group(1)
            # Extract bullet points
            for line in pattern_text.split('\n'):
                if line.strip().startswith(('-', '*', '•')):
                    patterns.append(line.strip().lstrip('-*• '))

        return patterns[:5]  # Top 5 patterns

    def _extract_gotchas(self, content: str) -> List[str]:
        """Extract gotchas/warnings from context."""
        gotchas = []

        # Look for gotchas/warnings/cautions section
        gotcha_match = re.search(
            r'##\s*(Gotchas?|Warnings?|Cautions?)\s*\n+(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if gotcha_match:
            gotcha_text = gotcha_match.group(2)
            # Extract bullet points
            for line in gotcha_text.split('\n'):
                if line.strip().startswith(('-', '*', '•')):
                    gotchas.append(line.strip().lstrip('-*• '))

        return gotchas[:5]  # Top 5 gotchas

    def generate_context_brief(self, objectives: List[str]) -> str:
        """
        Generate a brief including relevant context.

        Args:
            objectives: Session objectives

        Returns:
            Formatted brief string
        """
        relevant_contexts = self.find_relevant_context(objectives)

        if not relevant_contexts:
            return "ℹ️  No claude.md context files found in repository."

        brief_parts = [
            "📚 CODEBASE CONTEXT",
            "=" * 50,
            ""
        ]

        for context_path in relevant_contexts[:5]:  # Top 5 most relevant
            context = self.read_context(context_path)

            if "error" in context:
                continue

            relative_path = context["relative_path"]
            brief_parts.append(f"📁 {relative_path.parent}/")
            brief_parts.append(f"   {context['summary']}")

            if context.get('patterns'):
                brief_parts.append(f"   Patterns: {', '.join(context['patterns'][:3])}")

            if context.get('gotchas'):
                brief_parts.append(f"   ⚠️  {context['gotchas'][0]}")

            brief_parts.append("")

        brief_parts.append(f"💡 Tip: Full context in {len(relevant_contexts)} claude.md files")
        brief_parts.append("")

        return '\n'.join(brief_parts)

    def check_context_health(self, directories: List[Path]) -> Dict[str, any]:
        """
        Check context health for specific directories.

        Args:
            directories: List of directory paths to check

        Returns:
            Health report dictionary
        """
        report = {
            "healthy": [],
            "stale": [],
            "missing": []
        }

        for directory in directories:
            context_file = directory / "claude.md"

            if not context_file.exists():
                report["missing"].append(str(directory.relative_to(self.repo_path)))
                continue

            # Check staleness (simple: >30 days = stale)
            try:
                import time
                age_days = (time.time() - context_file.stat().st_mtime) / 86400

                if age_days > 30:
                    report["stale"].append({
                        "path": str(directory.relative_to(self.repo_path)),
                        "age_days": int(age_days)
                    })
                else:
                    report["healthy"].append(str(directory.relative_to(self.repo_path)))
            except Exception:
                pass

        return report


if __name__ == "__main__":
    # Test the context loader
    loader = ContextLoader()

    print("Context Loader Test")
    print("=" * 50)

    # Find all contexts
    all_contexts = loader.find_all_context_files()
    print(f"\nFound {len(all_contexts)} claude.md files")

    # Test with sample objectives
    objectives = ["Add authentication", "API integration"]
    print(f"\nObjectives: {objectives}")

    relevant = loader.find_relevant_context(objectives)
    print(f"Relevant contexts: {len(relevant)}")

    # Generate brief
    brief = loader.generate_context_brief(objectives)
    print("\n" + brief)
