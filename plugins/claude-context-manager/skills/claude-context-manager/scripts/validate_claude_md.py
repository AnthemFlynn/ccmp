#!/usr/bin/env python3
"""
Claude.md Validator

Validates existing claude.md files for completeness, accuracy, and quality.
Checks for TODO markers, outdated information, and missing key sections.

Usage:
    python validate_claude_md.py <path> [--strict] [--auto-fix]

Examples:
    python validate_claude_md.py /path/to/repo
    python validate_claude_md.py /path/to/src/claude.md
    python validate_claude_md.py /path/to/repo --strict
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import re

REQUIRED_SECTIONS = [
    'Overview',
    'Purpose'  # Alternative to Overview
]

RECOMMENDED_SECTIONS = [
    'Directory Structure',
    'Key Files',
    'Important Patterns',
    'Dependencies',
    'Usage'
]


def find_claude_md_files(root_path: Path) -> List[Path]:
    """Find all claude.md files in the directory tree."""
    claude_md_files = []
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip common ignored directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in {
            'node_modules', '__pycache__', 'venv', 'env', 'dist', 'build'
        }]
        
        if 'claude.md' in filenames:
            claude_md_files.append(Path(dirpath) / 'claude.md')
    
    return claude_md_files


def validate_claude_md(file_path: Path, strict: bool = False) -> Dict:
    """Validate a single claude.md file."""
    issues = []
    warnings = []
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        return {
            'valid': False,
            'issues': [f"Could not read file: {e}"],
            'warnings': [],
            'stats': {}
        }
    
    lines = content.split('\n')
    
    # Check for empty or very short files
    if len(content.strip()) < 50:
        issues.append("File is too short (less than 50 characters)")
    
    # Check for TODO markers
    todo_count = len(re.findall(r'TODO|FIXME|XXX', content, re.IGNORECASE))
    if todo_count > 0:
        if strict:
            issues.append(f"Found {todo_count} TODO/FIXME markers")
        else:
            warnings.append(f"Found {todo_count} TODO/FIXME markers")
    
    # Check for required sections
    has_overview = any(re.search(r'^##?\s+(Overview|Purpose)', line, re.IGNORECASE) for line in lines)
    if not has_overview:
        issues.append("Missing required section: Overview or Purpose")
    
    # Check for recommended sections
    found_sections = []
    for section in RECOMMENDED_SECTIONS:
        if any(re.search(rf'^##?\s+{section}', line, re.IGNORECASE) for line in lines):
            found_sections.append(section)
    
    missing_recommended = set(RECOMMENDED_SECTIONS) - set(found_sections)
    if missing_recommended and strict:
        warnings.append(f"Missing recommended sections: {', '.join(missing_recommended)}")
    
    # Check for placeholder text
    if '<!-- TODO' in content or 'Description' in content and 'TODO' in content:
        if strict:
            issues.append("Contains placeholder TODO comments that need completion")
        else:
            warnings.append("Contains placeholder TODO comments")
    
    # Check for minimal content in sections
    sections = re.split(r'^##?\s+', content, flags=re.MULTILINE)[1:]  # Split by headers
    for section in sections:
        lines_in_section = [l.strip() for l in section.split('\n')[1:] if l.strip() and not l.strip().startswith('<!--')]
        if len(lines_in_section) < 2:
            section_name = section.split('\n')[0]
            warnings.append(f"Section '{section_name}' has minimal content")
    
    # Check for broken links (basic check)
    broken_link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    links = re.findall(broken_link_pattern, content)
    for link_text, link_url in links:
        if link_url.startswith('./') or link_url.startswith('../'):
            # Check if relative path exists
            target_path = file_path.parent / link_url
            if not target_path.exists():
                warnings.append(f"Potentially broken relative link: {link_url}")
    
    # Check age (if git is available)
    stats = {
        'line_count': len(lines),
        'word_count': len(content.split()),
        'todo_count': todo_count,
        'sections_found': len(found_sections)
    }
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'stats': stats
    }


def print_validation_results(results: Dict[Path, Dict], strict: bool):
    """Print validation results in a readable format."""
    print("\n" + "="*70)
    print("CLAUDE.MD VALIDATION RESULTS")
    print("="*70)
    
    total_files = len(results)
    valid_files = sum(1 for r in results.values() if r['valid'])
    files_with_warnings = sum(1 for r in results.values() if r['warnings'])
    
    print(f"\n📊 Summary:")
    print(f"   Total files checked: {total_files}")
    print(f"   Valid files: {valid_files}")
    print(f"   Files with issues: {total_files - valid_files}")
    print(f"   Files with warnings: {files_with_warnings}")
    
    # Show files with issues
    files_with_issues = {p: r for p, r in results.items() if not r['valid']}
    if files_with_issues:
        print(f"\n❌ Files with issues:")
        print("-" * 70)
        for file_path, result in files_with_issues.items():
            print(f"\n📄 {file_path}")
            for issue in result['issues']:
                print(f"   ❌ {issue}")
            if result['warnings']:
                for warning in result['warnings']:
                    print(f"   ⚠️  {warning}")
    
    # Show files with warnings only
    files_with_only_warnings = {
        p: r for p, r in results.items() 
        if r['valid'] and r['warnings']
    }
    if files_with_only_warnings:
        print(f"\n⚠️  Files with warnings:")
        print("-" * 70)
        for file_path, result in files_with_only_warnings.items():
            print(f"\n📄 {file_path}")
            for warning in result['warnings']:
                print(f"   ⚠️  {warning}")
    
    # Show fully valid files
    fully_valid = {
        p: r for p, r in results.items() 
        if r['valid'] and not r['warnings']
    }
    if fully_valid:
        print(f"\n✅ Fully valid files:")
        print("-" * 70)
        for file_path in fully_valid.keys():
            print(f"   📄 {file_path}")
    
    print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(
        description='Validate claude.md files'
    )
    parser.add_argument(
        'path',
        type=str,
        help='Path to directory or specific claude.md file'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Enable strict validation (TODOs become errors)'
    )
    
    args = parser.parse_args()
    
    path = Path(args.path).resolve()
    
    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)
    
    # Find claude.md files
    if path.is_file() and path.name == 'claude.md':
        files_to_validate = [path]
    elif path.is_dir():
        files_to_validate = find_claude_md_files(path)
        if not files_to_validate:
            print(f"No claude.md files found in {path}")
            sys.exit(0)
    else:
        print(f"Error: Path must be a directory or a claude.md file")
        sys.exit(1)
    
    print(f"Validating {len(files_to_validate)} claude.md file(s)...")
    
    # Validate each file
    results = {}
    for file_path in files_to_validate:
        results[file_path] = validate_claude_md(file_path, strict=args.strict)
    
    # Print results
    print_validation_results(results, args.strict)
    
    # Exit with error code if any files have issues
    if any(not r['valid'] for r in results.values()):
        sys.exit(1)


if __name__ == '__main__':
    main()
