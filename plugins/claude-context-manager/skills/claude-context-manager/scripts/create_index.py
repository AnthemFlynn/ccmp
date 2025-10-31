#!/usr/bin/env python3
"""
Claude.md Index Creator

Creates or updates a master index of all claude.md files in a repository.
Useful for understanding the documentation structure at a glance.

Usage:
    python create_index.py <repo_path> [--output FILE] [--format FORMAT]

Examples:
    python create_index.py /path/to/repo
    python create_index.py /path/to/repo --output CLAUDE_INDEX.md
    python create_index.py /path/to/repo --format tree
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict
import re


def find_claude_md_files(root_path: Path) -> List[Path]:
    """Find all claude.md files, maintaining relative paths."""
    claude_md_files = []
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip common ignored directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in {
            'node_modules', '__pycache__', 'venv', 'env', 'dist', 'build'
        }]
        
        if 'claude.md' in filenames:
            full_path = Path(dirpath) / 'claude.md'
            claude_md_files.append(full_path)
    
    return sorted(claude_md_files)


def extract_title_and_overview(file_path: Path) -> Dict[str, str]:
    """Extract the title and first line of overview from a claude.md file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Extract title (first H1 header)
        title = None
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        # Extract first meaningful line after Overview section
        overview = None
        in_overview = False
        for line in lines:
            if re.match(r'^##?\s+(Overview|Purpose)', line, re.IGNORECASE):
                in_overview = True
                continue
            if in_overview:
                stripped = line.strip()
                # Skip empty lines and comments
                if stripped and not stripped.startswith('<!--') and not stripped.startswith('#'):
                    overview = stripped
                    break
                # Stop at next section
                if stripped.startswith('##'):
                    break
        
        return {
            'title': title or 'Untitled',
            'overview': overview or 'No overview available'
        }
    except Exception as e:
        return {
            'title': 'Error reading file',
            'overview': str(e)
        }


def create_tree_format(root_path: Path, files: List[Path]) -> str:
    """Create a tree-style index."""
    lines = ["# Claude.md Index", "", "Repository documentation structure:", ""]
    
    # Group files by directory depth
    for file_path in files:
        rel_path = file_path.relative_to(root_path)
        dir_path = rel_path.parent
        
        # Calculate depth
        depth = len(dir_path.parts)
        indent = "  " * depth
        
        # Get metadata
        metadata = extract_title_and_overview(file_path)
        
        # Format entry
        dir_display = str(dir_path) if str(dir_path) != '.' else '(root)'
        lines.append(f"{indent}📁 **{dir_display}** ([claude.md]({rel_path}))")
        lines.append(f"{indent}   {metadata['title']}")
        lines.append("")
    
    return "\n".join(lines)


def create_table_format(root_path: Path, files: List[Path]) -> str:
    """Create a table-style index."""
    lines = [
        "# Claude.md Index",
        "",
        "| Directory | Title | Overview |",
        "|-----------|-------|----------|"
    ]
    
    for file_path in files:
        rel_path = file_path.relative_to(root_path)
        dir_path = rel_path.parent
        dir_display = str(dir_path) if str(dir_path) != '.' else '(root)'
        
        metadata = extract_title_and_overview(file_path)
        
        # Truncate overview if too long
        overview = metadata['overview']
        if len(overview) > 80:
            overview = overview[:77] + "..."
        
        # Escape pipe characters
        title = metadata['title'].replace('|', '\\|')
        overview = overview.replace('|', '\\|')
        
        lines.append(f"| [{dir_display}]({rel_path}) | {title} | {overview} |")
    
    return "\n".join(lines)


def create_detailed_format(root_path: Path, files: List[Path]) -> str:
    """Create a detailed list-style index."""
    lines = ["# Claude.md Index", "", "Complete documentation map for this repository.", ""]
    
    for i, file_path in enumerate(files, 1):
        rel_path = file_path.relative_to(root_path)
        dir_path = rel_path.parent
        dir_display = str(dir_path) if str(dir_path) != '.' else '(root)'
        
        metadata = extract_title_and_overview(file_path)
        
        lines.append(f"## {i}. {dir_display}")
        lines.append("")
        lines.append(f"**File:** [{rel_path}]({rel_path})")
        lines.append("")
        lines.append(f"**Title:** {metadata['title']}")
        lines.append("")
        lines.append(f"**Overview:** {metadata['overview']}")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Create an index of all claude.md files in a repository'
    )
    parser.add_argument(
        'repo_path',
        type=str,
        help='Path to repository root'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='CLAUDE_INDEX.md',
        help='Output filename (default: CLAUDE_INDEX.md)'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['tree', 'table', 'detailed'],
        default='tree',
        help='Index format (default: tree)'
    )
    
    args = parser.parse_args()
    
    repo_path = Path(args.repo_path).resolve()
    
    if not repo_path.exists():
        print(f"Error: Path does not exist: {repo_path}")
        sys.exit(1)
    
    if not repo_path.is_dir():
        print(f"Error: Path is not a directory: {repo_path}")
        sys.exit(1)
    
    print(f"Scanning repository: {repo_path}")
    files = find_claude_md_files(repo_path)
    
    if not files:
        print("No claude.md files found in repository.")
        sys.exit(0)
    
    print(f"Found {len(files)} claude.md file(s)")
    
    # Generate index
    if args.format == 'tree':
        content = create_tree_format(repo_path, files)
    elif args.format == 'table':
        content = create_table_format(repo_path, files)
    else:  # detailed
        content = create_detailed_format(repo_path, files)
    
    # Write output
    output_path = repo_path / args.output
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Created index: {output_path}")


if __name__ == '__main__':
    main()
