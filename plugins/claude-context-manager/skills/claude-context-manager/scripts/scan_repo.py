#!/usr/bin/env python3
"""
Repository Scanner for claude.md Management

Analyzes repository structure and suggests where claude.md files should exist.
Helps identify directories that need documentation.

Usage:
    python scan_repo.py <repo_path> [--min-files N] [--show-existing]

Examples:
    python scan_repo.py /path/to/repo
    python scan_repo.py /path/to/repo --min-files 3
    python scan_repo.py /path/to/repo --show-existing
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Set

# Directories to ignore
IGNORE_DIRS = {
    '.git', '.github', 'node_modules', '__pycache__', '.pytest_cache',
    'venv', 'env', '.venv', 'dist', 'build', '.egg-info', 'coverage',
    '.tox', '.mypy_cache', '.ruff_cache', 'target', 'bin', 'obj'
}

# File extensions to consider when calculating "significance"
SIGNIFICANT_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.cpp',
    '.c', '.h', '.hpp', '.cs', '.rb', '.php', '.swift', '.kt', '.scala',
    '.sh', '.bash', '.md', '.yaml', '.yml', '.json', '.toml', '.xml'
}


def scan_directory(root_path: Path, min_files: int = 2) -> Dict:
    """
    Scan directory tree and identify directories that should have claude.md files.
    
    Args:
        root_path: Root directory to scan
        min_files: Minimum number of significant files to warrant a claude.md
    
    Returns:
        Dictionary with analysis results
    """
    results = {
        'needs_claude_md': [],
        'has_claude_md': [],
        'stats': {
            'total_dirs': 0,
            'dirs_scanned': 0,
            'significant_dirs': 0
        }
    }
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Filter out ignored directories
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        
        results['stats']['total_dirs'] += 1
        current_path = Path(dirpath)
        
        # Check if this directory has claude.md
        has_claude_md = 'claude.md' in filenames
        
        # Count significant files
        significant_files = [
            f for f in filenames
            if Path(f).suffix in SIGNIFICANT_EXTENSIONS and f != 'claude.md'
        ]
        
        # Determine if this directory is "significant" enough
        is_significant = len(significant_files) >= min_files
        
        if is_significant:
            results['stats']['significant_dirs'] += 1
            results['stats']['dirs_scanned'] += 1
            
            rel_path = current_path.relative_to(root_path)
            dir_info = {
                'path': str(rel_path) if str(rel_path) != '.' else '(root)',
                'file_count': len(significant_files),
                'file_types': sorted(set(Path(f).suffix for f in significant_files))
            }
            
            if has_claude_md:
                results['has_claude_md'].append(dir_info)
            else:
                results['needs_claude_md'].append(dir_info)
    
    return results


def print_results(results: Dict, show_existing: bool = False):
    """Print scan results in a readable format."""
    stats = results['stats']
    
    print("\n" + "="*70)
    print("REPOSITORY SCAN RESULTS")
    print("="*70)
    
    print(f"\n📊 Statistics:")
    print(f"   Total directories: {stats['total_dirs']}")
    print(f"   Significant directories: {stats['significant_dirs']}")
    print(f"   Directories with claude.md: {len(results['has_claude_md'])}")
    print(f"   Directories needing claude.md: {len(results['needs_claude_md'])}")
    
    if results['needs_claude_md']:
        print(f"\n❌ Directories that should have claude.md:")
        print("-" * 70)
        for dir_info in results['needs_claude_md']:
            print(f"\n📁 {dir_info['path']}")
            print(f"   Files: {dir_info['file_count']}")
            print(f"   Types: {', '.join(dir_info['file_types'])}")
    
    if show_existing and results['has_claude_md']:
        print(f"\n✅ Directories with existing claude.md:")
        print("-" * 70)
        for dir_info in results['has_claude_md']:
            print(f"\n📁 {dir_info['path']}")
            print(f"   Files: {dir_info['file_count']}")
            print(f"   Types: {', '.join(dir_info['file_types'])}")
    
    print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(
        description='Scan repository for claude.md file coverage'
    )
    parser.add_argument(
        'repo_path',
        type=str,
        help='Path to repository root'
    )
    parser.add_argument(
        '--min-files',
        type=int,
        default=2,
        help='Minimum significant files to warrant a claude.md (default: 2)'
    )
    parser.add_argument(
        '--show-existing',
        action='store_true',
        help='Show directories that already have claude.md files'
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
    results = scan_directory(repo_path, args.min_files)
    print_results(results, args.show_existing)


if __name__ == '__main__':
    main()
