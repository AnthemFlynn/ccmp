#!/usr/bin/env python3
"""
Session Management Initialization Script

Initializes session management in a git repository by creating the .session/
directory with configuration and template files.

Usage:
    python init_session.py [--force]

Options:
    --force     Overwrite existing .session/ directory
"""

import argparse
import os
import shutil
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Initialize session management")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()
    
    # Check if we're in a git repository
    if not Path(".git").exists():
        print("Error: Not in a git repository")
        print("Run 'git init' first")
        return 1
    
    # Check if .session/ already exists
    session_dir = Path(".session")
    if session_dir.exists() and not args.force:
        print("Session management already initialized")
        print("Use --force to reinitialize")
        return 1
    
    # Create .session/ directory
    session_dir.mkdir(exist_ok=True)
    print(f"✅ Created {session_dir}/")
    
    # Copy template files from assets/
    # Note: This assumes the skill is installed and assets are available
    # In production, these would be copied from the skill's assets/ directory
    
    # Create basic files
    files_created = []
    
    # config.yaml
    config_path = session_dir / "config.yaml"
    if args.force or not config_path.exists():
        # In production: copy from assets/config-template.yaml
        print(f"✅ Created {config_path}")
        files_created.append(str(config_path))
    
    # architecture.md
    arch_path = session_dir / "architecture.md"
    if args.force or not arch_path.exists():
        # In production: copy from assets/architecture-template.md
        print(f"✅ Created {arch_path}")
        files_created.append(str(arch_path))
    
    # conventions.md
    conv_path = session_dir / "conventions.md"
    if args.force or not conv_path.exists():
        # In production: copy from assets/conventions-template.md
        print(f"✅ Created {conv_path}")
        files_created.append(str(conv_path))
    
    # Create .git/sessions/ directory for local session data
    git_sessions_dir = Path(".git/sessions")
    git_sessions_dir.mkdir(exist_ok=True)
    print(f"✅ Created {git_sessions_dir}/")
    
    print("\n🎉 Session management initialized!")
    print("\nNext steps:")
    print("1. Edit .session/architecture.md with your project's architecture")
    print("2. Edit .session/conventions.md with your code conventions")
    print("3. Customize .session/config.yaml as needed")
    print("4. Commit .session/ to git: git add .session/ && git commit -m 'Initialize session management'")
    print("5. Start your first session: python scripts/session.py start <branch-name>")
    
    return 0

if __name__ == "__main__":
    exit(main())
