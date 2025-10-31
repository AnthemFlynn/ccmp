#!/usr/bin/env python3
"""
Auto-Update Context - Intelligent Context Synchronization

Analyzes code changes and autonomously updates context files.
Designed to be run by Claude with minimal supervision.

Usage:
    python auto_update.py <directory_path> [--analyze-only] [--verbose]
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
import subprocess
import re

def get_recent_changes(dir_path: Path, since_days: int = 30) -> Dict:
    """Get summary of recent changes in directory."""
    try:
        # Get changed files
        result = subprocess.run(
            ['git', 'diff', '--name-status', f'HEAD~{since_days*4}', 'HEAD', '--', str(dir_path)],
            cwd=dir_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {'files_changed': [], 'summary': {}}
        
        changes = result.stdout.strip().split('\n')
        
        added = []
        modified = []
        deleted = []
        
        for change in changes:
            if not change:
                continue
            parts = change.split('\t', 1)
            if len(parts) != 2:
                continue
            status, filepath = parts
            
            if status.startswith('A'):
                added.append(filepath)
            elif status.startswith('M'):
                modified.append(filepath)
            elif status.startswith('D'):
                deleted.append(filepath)
        
        return {
            'files_changed': added + modified + deleted,
            'summary': {
                'added': len(added),
                'modified': len(modified),
                'deleted': len(deleted)
            },
            'details': {
                'added': added,
                'modified': modified,
                'deleted': deleted
            }
        }
    except:
        return {'files_changed': [], 'summary': {}}

def analyze_code_patterns(dir_path: Path) -> Dict:
    """Analyze current code patterns in directory."""
    patterns = {
        'file_types': {},
        'common_imports': set(),
        'naming_patterns': [],
        'frameworks_detected': set()
    }
    
    # Analyze files
    for item in dir_path.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            ext = item.suffix
            patterns['file_types'][ext] = patterns['file_types'].get(ext, 0) + 1
            
            # Analyze imports for common patterns
            if ext in ['.py', '.js', '.ts', '.jsx', '.tsx']:
                try:
                    content = item.read_text()
                    
                    # Python imports
                    if ext == '.py':
                        imports = re.findall(r'^\s*(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_]*)', content, re.MULTILINE)
                        patterns['common_imports'].update(imports[:5])  # Top 5
                        
                        # Detect frameworks
                        if 'fastapi' in content.lower():
                            patterns['frameworks_detected'].add('FastAPI')
                        if 'flask' in content.lower():
                            patterns['frameworks_detected'].add('Flask')
                    
                    # JavaScript/TypeScript imports
                    elif ext in ['.js', '.ts', '.jsx', '.tsx']:
                        imports = re.findall(r'(?:from|require\()\s*[\'"]([^\'\"]+)', content)
                        patterns['common_imports'].update(imports[:5])
                        
                        # Detect frameworks
                        if 'react' in content.lower():
                            patterns['frameworks_detected'].add('React')
                        if 'express' in content.lower():
                            patterns['frameworks_detected'].add('Express')
                        if 'vue' in content.lower():
                            patterns['frameworks_detected'].add('Vue')
                except:
                    pass
    
    patterns['common_imports'] = list(patterns['common_imports'])
    patterns['frameworks_detected'] = list(patterns['frameworks_detected'])
    
    return patterns

def read_existing_context(context_file: Path) -> str:
    """Read existing context file."""
    if context_file.exists():
        return context_file.read_text()
    return ""

def needs_update(existing_context: str, current_patterns: Dict, recent_changes: Dict) -> Dict:
    """Determine if context needs updating and what sections."""
    update_needed = {
        'should_update': False,
        'reasons': [],
        'sections_to_update': []
    }
    
    # Check if significant changes occurred
    total_changes = recent_changes['summary'].get('added', 0) + \
                   recent_changes['summary'].get('modified', 0) + \
                   recent_changes['summary'].get('deleted', 0)
    
    if total_changes > 5:
        update_needed['should_update'] = True
        update_needed['reasons'].append(f'{total_changes} files changed')
        update_needed['sections_to_update'].append('File Types')
        update_needed['sections_to_update'].append('Key Files')
    
    # Check if frameworks mentioned in context match detected
    for framework in current_patterns.get('frameworks_detected', []):
        if framework not in existing_context:
            update_needed['should_update'] = True
            update_needed['reasons'].append(f'New framework detected: {framework}')
            update_needed['sections_to_update'].append('Important Patterns')
    
    # Check if context has TODO markers
    if 'TODO' in existing_context or '<!-- TODO' in existing_context:
        update_needed['should_update'] = True
        update_needed['reasons'].append('Context has TODO markers')
        update_needed['sections_to_update'].append('All incomplete sections')
    
    # Check age (if very old, likely needs update)
    if existing_context and len(existing_context) < 200:
        update_needed['should_update'] = True
        update_needed['reasons'].append('Context is minimal')
        update_needed['sections_to_update'].append('Overview')
    
    return update_needed

def generate_updated_sections(existing_context: str, current_patterns: Dict, recent_changes: Dict) -> Dict:
    """Generate suggestions for updated context sections."""
    suggestions = {}
    
    # File Types section
    if current_patterns['file_types']:
        file_types_text = []
        for ext, count in sorted(current_patterns['file_types'].items()):
            file_types_text.append(f"- **{ext}** ({count} files): [Describe purpose of these files]")
        suggestions['File Types'] = "\n".join(file_types_text)
    
    # Frameworks/Patterns section
    if current_patterns['frameworks_detected']:
        frameworks_text = []
        frameworks_text.append("**Frameworks in use:**")
        for fw in current_patterns['frameworks_detected']:
            frameworks_text.append(f"- {fw}")
        suggestions['Frameworks'] = "\n".join(frameworks_text)
    
    # Recent changes section
    if recent_changes['summary']:
        changes_text = []
        changes_text.append("**Recent activity:**")
        s = recent_changes['summary']
        if s.get('added'):
            changes_text.append(f"- {s['added']} files added")
        if s.get('modified'):
            changes_text.append(f"- {s['modified']} files modified")
        if s.get('deleted'):
            changes_text.append(f"- {s['deleted']} files deleted")
        suggestions['Recent Changes'] = "\n".join(changes_text)
    
    return suggestions

def format_update_report(dir_path: Path, update_analysis: Dict, suggestions: Dict, analyze_only: bool) -> str:
    """Format update report for Claude to read."""
    lines = []
    lines.append("=" * 70)
    lines.append("CONTEXT UPDATE ANALYSIS")
    lines.append("=" * 70)
    lines.append(f"\nDirectory: {dir_path}")
    lines.append(f"Timestamp: {datetime.now().isoformat()}")
    lines.append(f"\nMode: {'ANALYZE ONLY' if analyze_only else 'UPDATE READY'}")
    
    if update_analysis['should_update']:
        lines.append("\n✅ UPDATE RECOMMENDED")
        lines.append("\nReasons:")
        for reason in update_analysis['reasons']:
            lines.append(f"  • {reason}")
        
        lines.append("\nSections to update:")
        for section in update_analysis['sections_to_update']:
            lines.append(f"  • {section}")
        
        if suggestions:
            lines.append("\n" + "=" * 70)
            lines.append("SUGGESTED UPDATES")
            lines.append("=" * 70)
            
            for section_name, content in suggestions.items():
                lines.append(f"\n## {section_name}\n")
                lines.append(content)
    else:
        lines.append("\n✓ Context appears current")
        lines.append("No immediate updates needed")
    
    lines.append("\n" + "=" * 70)
    return "\n".join(lines)

def update_context_file(context_file: Path, suggestions: Dict, existing_context: str) -> bool:
    """Update context file with new information."""
    # This is a smart merge - preserve existing content, update specific sections
    # For now, append suggestions as new sections if they don't exist
    
    updated_content = existing_context
    
    # Add a separator before updates
    updated_content += "\n\n---\n*Updated: {}*\n".format(datetime.now().strftime("%Y-%m-%d"))
    
    # Add suggested updates
    for section_name, content in suggestions.items():
        if section_name not in existing_context:
            updated_content += f"\n## {section_name}\n\n{content}\n"
    
    # Write back
    try:
        context_file.write_text(updated_content)
        return True
    except Exception as e:
        print(f"Error writing context file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Autonomously update context based on code changes'
    )
    parser.add_argument('directory', type=str, help='Directory to analyze')
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Only analyze, do not update'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force update even if no changes detected'
    )
    
    args = parser.parse_args()
    dir_path = Path(args.directory).resolve()
    
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"Error: Invalid directory: {dir_path}")
        sys.exit(1)
    
    context_file = dir_path / 'claude.md'
    
    # Analyze current state
    print("Analyzing directory..." if args.verbose else "", end='')
    recent_changes = get_recent_changes(dir_path)
    current_patterns = analyze_code_patterns(dir_path)
    existing_context = read_existing_context(context_file)
    print(" Done." if args.verbose else "")
    
    # Determine if update needed
    update_analysis = needs_update(existing_context, current_patterns, recent_changes)
    
    if args.force:
        update_analysis['should_update'] = True
        update_analysis['reasons'].append('Forced update')
    
    # Generate suggestions
    suggestions = generate_updated_sections(existing_context, current_patterns, recent_changes)
    
    # Output report
    report = format_update_report(dir_path, update_analysis, suggestions, args.analyze_only)
    print(report)
    
    # Perform update if not analyze-only
    if update_analysis['should_update'] and not args.analyze_only:
        print("\nUpdating context file...")
        if update_context_file(context_file, suggestions, existing_context):
            print(f"✅ Updated: {context_file}")
        else:
            print(f"❌ Failed to update: {context_file}")
            sys.exit(1)
    
    sys.exit(0 if update_analysis['should_update'] else 0)

if __name__ == '__main__':
    main()
