#!/usr/bin/env python3
"""
Claude.md Generator

Analyzes a directory and generates an appropriate claude.md file with context
about the directory's purpose, structure, and key files.

Usage:
    python generate_claude_md.py <directory_path> [--output FILE] [--analyze-depth N]

Examples:
    python generate_claude_md.py /path/to/src
    python generate_claude_md.py /path/to/tests --output claude.md
    python generate_claude_md.py /path/to/api --analyze-depth 1
"""

import os
import sys
import argparse
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Set
import subprocess

IGNORE_DIRS = {
    '.git', '.github', 'node_modules', '__pycache__', '.pytest_cache',
    'venv', 'env', '.venv', 'dist', 'build', '.egg-info', 'coverage'
}


def analyze_directory(dir_path: Path, depth: int = 0, max_depth: int = 1) -> Dict:
    """Analyze directory structure and content."""
    analysis = {
        'path': dir_path,
        'files_by_type': defaultdict(list),
        'subdirs': [],
        'total_files': 0,
        'key_files': []
    }
    
    # Key files to look for
    key_filenames = {
        'README.md', 'README.rst', 'README.txt',
        'main.py', 'app.py', 'index.py', '__init__.py',
        'index.js', 'index.ts', 'main.js', 'main.ts',
        'package.json', 'setup.py', 'pyproject.toml',
        'Cargo.toml', 'pom.xml', 'build.gradle',
        'Makefile', 'CMakeLists.txt'
    }
    
    try:
        items = list(dir_path.iterdir())
    except PermissionError:
        return analysis
    
    for item in items:
        if item.name.startswith('.') and item.name not in {'.gitignore', '.env.example'}:
            continue
        
        if item.is_file():
            analysis['total_files'] += 1
            ext = item.suffix or 'no_extension'
            analysis['files_by_type'][ext].append(item.name)
            
            if item.name in key_filenames:
                analysis['key_files'].append(item.name)
        
        elif item.is_dir() and item.name not in IGNORE_DIRS:
            analysis['subdirs'].append(item.name)
    
    return analysis


def infer_directory_purpose(dir_name: str, analysis: Dict) -> str:
    """Infer the purpose of a directory based on its name and contents."""
    dir_name_lower = dir_name.lower()
    
    # Common patterns
    purposes = {
        'src': 'source code',
        'lib': 'library code',
        'app': 'application code',
        'api': 'API implementation',
        'tests': 'test suite',
        'test': 'test suite',
        'docs': 'documentation',
        'documentation': 'documentation',
        'scripts': 'utility scripts',
        'utils': 'utility functions',
        'helpers': 'helper functions',
        'models': 'data models',
        'views': 'view templates',
        'controllers': 'controllers',
        'routes': 'route definitions',
        'components': 'reusable components',
        'services': 'service layer',
        'middleware': 'middleware functions',
        'config': 'configuration files',
        'public': 'public assets',
        'static': 'static assets',
        'assets': 'static assets',
        'migrations': 'database migrations',
        'fixtures': 'test fixtures',
        'examples': 'example code',
    }
    
    for pattern, purpose in purposes.items():
        if pattern in dir_name_lower:
            return purpose
    
    # Infer from file types
    file_types = set(analysis['files_by_type'].keys())
    
    if '.test.py' in str(analysis['files_by_type']) or '.test.js' in str(analysis['files_by_type']):
        return 'test suite'
    
    if any('.md' in ext or '.rst' in ext for ext in file_types):
        return 'documentation'
    
    return 'implementation'


def generate_claude_md(dir_path: Path, analyze_depth: int = 1) -> str:
    """Generate claude.md content for a directory."""
    analysis = analyze_directory(dir_path, max_depth=analyze_depth)
    dir_name = dir_path.name if dir_path.name else 'root'
    purpose = infer_directory_purpose(dir_name, analysis)
    
    # Build the claude.md content
    content = []
    
    # Header
    content.append(f"# {dir_name}/")
    content.append("")
    
    # Purpose section
    content.append(f"This directory contains the {purpose}.")
    content.append("")
    
    # Overview section
    content.append("## Overview")
    content.append("")
    content.append(f"<!-- TODO: Add detailed description of what this directory contains and its role in the project -->")
    content.append("")
    
    # Structure section if there are subdirectories
    if analysis['subdirs']:
        content.append("## Directory Structure")
        content.append("")
        content.append("```")
        content.append(f"{dir_name}/")
        for subdir in sorted(analysis['subdirs'])[:10]:  # Limit to first 10
            content.append(f"├── {subdir}/")
        if len(analysis['subdirs']) > 10:
            content.append(f"└── ... ({len(analysis['subdirs']) - 10} more)")
        content.append("```")
        content.append("")
    
    # Key files section
    if analysis['key_files']:
        content.append("## Key Files")
        content.append("")
        for key_file in sorted(analysis['key_files']):
            content.append(f"- **{key_file}**: <!-- TODO: Describe purpose -->")
        content.append("")
    
    # File types section
    if analysis['files_by_type']:
        content.append("## File Types")
        content.append("")
        for ext, files in sorted(analysis['files_by_type'].items()):
            if ext != 'no_extension':
                content.append(f"- **{ext}** ({len(files)} files): <!-- TODO: Describe purpose -->")
        content.append("")
    
    # Important patterns section
    content.append("## Important Patterns")
    content.append("")
    content.append("<!-- TODO: Document key patterns, conventions, or architectural decisions -->")
    content.append("")
    content.append("- Pattern 1: Description")
    content.append("- Pattern 2: Description")
    content.append("")
    
    # Dependencies section
    content.append("## Dependencies")
    content.append("")
    content.append("<!-- TODO: List key dependencies or relationships with other parts of the codebase -->")
    content.append("")
    
    # Usage/Entry Points section
    content.append("## Usage")
    content.append("")
    content.append("<!-- TODO: Explain how to use or interact with code in this directory -->")
    content.append("")
    
    # Notes section
    content.append("## Notes")
    content.append("")
    content.append("<!-- TODO: Add any additional context, gotchas, or important information -->")
    content.append("")
    
    return "\n".join(content)


def main():
    parser = argparse.ArgumentParser(
        description='Generate claude.md file for a directory'
    )
    parser.add_argument(
        'directory',
        type=str,
        help='Path to directory'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='claude.md',
        help='Output filename (default: claude.md)'
    )
    parser.add_argument(
        '--analyze-depth',
        type=int,
        default=1,
        help='How deep to analyze subdirectories (default: 1)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing claude.md file'
    )
    
    args = parser.parse_args()
    
    dir_path = Path(args.directory).resolve()
    
    if not dir_path.exists():
        print(f"Error: Directory does not exist: {dir_path}")
        sys.exit(1)
    
    if not dir_path.is_dir():
        print(f"Error: Path is not a directory: {dir_path}")
        sys.exit(1)
    
    output_path = dir_path / args.output
    
    if output_path.exists() and not args.force:
        print(f"Error: {output_path} already exists. Use --force to overwrite.")
        sys.exit(1)
    
    print(f"Analyzing directory: {dir_path}")
    content = generate_claude_md(dir_path, args.analyze_depth)
    
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Generated {output_path}")
    print(f"\nNext steps:")
    print(f"1. Review the generated file and fill in TODO sections")
    print(f"2. Add specific details about the directory's purpose")
    print(f"3. Document key patterns and conventions")


if __name__ == '__main__':
    main()
