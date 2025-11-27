#!/usr/bin/env python3
"""
Context Monitor - Autonomous Context Health Checker

This script is designed to be run by Claude autonomously to monitor
context health and identify what needs attention.

Outputs structured data that Claude can interpret and act on.

Usage:
    python monitor.py <repo_path> [--format json|text]
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import subprocess

def get_git_last_modified(file_path: Path) -> Optional[datetime]:
    """Get the last git modification time for a file."""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%ai', str(file_path)],
            cwd=file_path.parent,
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return datetime.fromisoformat(result.stdout.strip().rsplit(' ', 1)[0])
    except:
        pass
    return None

def get_directory_last_modified(dir_path: Path) -> Optional[datetime]:
    """Get the last git modification time for any file in directory."""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%ai', '--', str(dir_path)],
            cwd=dir_path if dir_path.is_dir() else dir_path.parent,
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return datetime.fromisoformat(result.stdout.strip().rsplit(' ', 1)[0])
    except:
        pass
    return None

def count_commits_since(path: Path, since_date: datetime) -> int:
    """Count commits affecting path since a given date."""
    try:
        result = subprocess.run(
            ['git', 'rev-list', '--count', f'--since={since_date.isoformat()}', 'HEAD', '--', str(path)],
            cwd=path if path.is_dir() else path.parent,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
    except:
        pass
    return 0

def calculate_staleness_score(context_age_days: int, commits_since_update: int) -> Dict:
    """Calculate staleness score and priority."""
    # Scoring algorithm
    age_score = min(context_age_days / 30, 3)  # Cap at 3 (90+ days)
    commit_score = min(commits_since_update / 10, 3)  # Cap at 3 (30+ commits)
    
    total_score = age_score + commit_score
    
    if total_score >= 4:
        priority = 'critical'
        action = 'UPDATE_NOW'
    elif total_score >= 2.5:
        priority = 'high'
        action = 'UPDATE_SOON'
    elif total_score >= 1.5:
        priority = 'medium'
        action = 'REVIEW'
    else:
        priority = 'low'
        action = 'MONITOR'
    
    return {
        'score': round(total_score, 2),
        'priority': priority,
        'action': action,
        'age_score': round(age_score, 2),
        'commit_score': round(commit_score, 2)
    }

def find_claude_md_files(root_path: Path) -> List[Path]:
    """Find all claude.md files."""
    claude_md_files = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in {
            'node_modules', '__pycache__', 'venv', 'env', 'dist', 'build'
        }]
        if 'claude.md' in filenames:
            claude_md_files.append(Path(dirpath) / 'claude.md')
    return sorted(claude_md_files)

def analyze_context_file(file_path: Path, root_path: Path) -> Dict:
    """Analyze a single context file for staleness."""
    now = datetime.now()
    
    # Get context file last modified
    context_modified = get_git_last_modified(file_path)
    if not context_modified:
        # Fall back to filesystem mtime
        context_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
    
    # Get directory last modified
    dir_path = file_path.parent
    dir_modified = get_directory_last_modified(dir_path)
    
    # Calculate age
    context_age = now - context_modified
    context_age_days = context_age.days
    
    # Count commits since context update
    commits_since_update = count_commits_since(dir_path, context_modified)
    
    # Calculate staleness
    staleness = calculate_staleness_score(context_age_days, commits_since_update)
    
    # Relative path for display
    rel_path = file_path.relative_to(root_path)
    
    return {
        'path': str(rel_path),
        'directory': str(rel_path.parent),
        'context_age_days': context_age_days,
        'context_last_updated': context_modified.isoformat(),
        'directory_last_modified': dir_modified.isoformat() if dir_modified else None,
        'commits_since_update': commits_since_update,
        'staleness': staleness,
        'needs_attention': staleness['action'] in ['UPDATE_NOW', 'UPDATE_SOON']
    }

def monitor_repository(repo_path: Path) -> Dict:
    """Monitor entire repository for context health."""
    files = find_claude_md_files(repo_path)
    
    if not files:
        return {
            'status': 'no_context_files',
            'message': 'No claude.md files found in repository',
            'files': []
        }
    
    analyses = [analyze_context_file(f, repo_path) for f in files]
    
    # Categorize by priority
    critical = [a for a in analyses if a['staleness']['priority'] == 'critical']
    high = [a for a in analyses if a['staleness']['priority'] == 'high']
    medium = [a for a in analyses if a['staleness']['priority'] == 'medium']
    low = [a for a in analyses if a['staleness']['priority'] == 'low']
    
    # Overall health score (0-100, higher is better)
    avg_staleness = sum(a['staleness']['score'] for a in analyses) / len(analyses)
    health_score = max(0, 100 - (avg_staleness * 20))
    
    return {
        'status': 'analyzed',
        'timestamp': datetime.now().isoformat(),
        'repository': str(repo_path),
        'summary': {
            'total_files': len(analyses),
            'critical': len(critical),
            'high': len(high),
            'medium': len(medium),
            'low': len(low),
            'health_score': round(health_score, 1)
        },
        'files': {
            'critical': critical,
            'high': high,
            'medium': medium,
            'low': low
        },
        'recommendations': generate_recommendations(critical, high, medium)
    }

def generate_recommendations(critical: List, high: List, medium: List) -> List[str]:
    """Generate action recommendations for Claude."""
    recommendations = []
    
    if critical:
        recommendations.append(
            f"IMMEDIATE ACTION: {len(critical)} context file(s) are critically stale. "
            f"Update: {', '.join([c['directory'] for c in critical[:3]])}"
        )
    
    if high:
        recommendations.append(
            f"HIGH PRIORITY: {len(high)} context file(s) need updating soon. "
            f"Review: {', '.join([h['directory'] for h in high[:3]])}"
        )
    
    if medium:
        recommendations.append(
            f"MEDIUM PRIORITY: {len(medium)} context file(s) should be reviewed. "
            f"Consider updating when convenient."
        )
    
    if not critical and not high:
        recommendations.append("All context files are reasonably current. Continue monitoring.")
    
    return recommendations

def format_text_output(data: Dict) -> str:
    """Format output as readable text for Claude."""
    lines = []
    lines.append("=" * 70)
    lines.append("CONTEXT HEALTH MONITOR")
    lines.append("=" * 70)
    
    if data['status'] == 'no_context_files':
        lines.append(f"\n{data['message']}")
        return "\n".join(lines)
    
    summary = data['summary']
    lines.append(f"\nRepository: {data['repository']}")
    lines.append(f"Timestamp: {data['timestamp']}")
    lines.append(f"\n📊 Health Score: {summary['health_score']}/100")
    lines.append(f"\n📁 Context Files: {summary['total_files']}")
    
    if summary['critical']:
        lines.append(f"   🔴 Critical: {summary['critical']}")
    if summary['high']:
        lines.append(f"   🟠 High: {summary['high']}")
    if summary['medium']:
        lines.append(f"   🟡 Medium: {summary['medium']}")
    if summary['low']:
        lines.append(f"   🟢 Low: {summary['low']}")
    
    lines.append("\n" + "=" * 70)
    lines.append("RECOMMENDATIONS")
    lines.append("=" * 70)
    
    for i, rec in enumerate(data['recommendations'], 1):
        lines.append(f"\n{i}. {rec}")
    
    # Show details for files needing attention
    needs_attention = data['files']['critical'] + data['files']['high']
    if needs_attention:
        lines.append("\n" + "=" * 70)
        lines.append("DETAILS - FILES NEEDING ATTENTION")
        lines.append("=" * 70)
        
        for file_data in needs_attention:
            lines.append(f"\n📁 {file_data['directory']}")
            lines.append(f"   Path: {file_data['path']}")
            lines.append(f"   Age: {file_data['context_age_days']} days")
            lines.append(f"   Commits since update: {file_data['commits_since_update']}")
            lines.append(f"   Priority: {file_data['staleness']['priority'].upper()}")
            lines.append(f"   Action: {file_data['staleness']['action']}")
    
    lines.append("\n" + "=" * 70)
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(
        description='Monitor context health and identify stale files'
    )
    parser.add_argument('repo_path', type=str, help='Repository path')
    parser.add_argument(
        '--format',
        choices=['json', 'text'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    repo_path = Path(args.repo_path).resolve()
    
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    # Analyze repository
    results = monitor_repository(repo_path)
    
    # Output results
    if args.format == 'json':
        print(json.dumps(results, indent=2))
    else:
        print(format_text_output(results))
    
    # Exit code based on health
    if results['status'] == 'analyzed':
        if results['summary']['critical'] > 0:
            sys.exit(2)  # Critical issues
        elif results['summary']['high'] > 0:
            sys.exit(1)  # High priority issues
    
    sys.exit(0)

if __name__ == '__main__':
    main()
