#!/usr/bin/env python3
"""
Session Management CLI

Main command-line interface for managing coding sessions.

Usage:
    python session.py <command> [options]

Commands:
    start       - Start new or resume existing session
    resume      - Resume current session
    checkpoint  - Create checkpoint
    end         - End session with handoff
    switch      - Switch to different session
    status      - Show session status
    history     - Show session history
    objectives  - Manage session objectives
    blockers    - Manage session blockers
    decisions   - Log architectural decisions
    analyze     - Analyze session metrics
    compare     - Compare sessions
    report      - Generate reports

For detailed command reference, see references/commands.md
"""

import argparse
import sys
from pathlib import Path
import subprocess

# Add lib to path for integration imports
repo_root = Path(__file__).resolve().parents[5]  # Go up to repo root
sys.path.insert(0, str(repo_root / "lib"))

try:
    from session_integration import SessionIntegration
    from ccmp_integration import CCMPIntegration, is_session_active, is_tdd_mode
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    print("⚠️  Integration libraries not found. Running in standalone mode.")

def check_session_initialized():
    """Check if session management is initialized"""
    if not Path(".session").exists():
        print("❌ Session management not initialized")
        print("Run: python scripts/init_session.py")
        return False
    return True

def get_current_branch():
    """Get current git branch"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_changed_directories():
    """Get directories with changes since last commit"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split('\n')
        directories = set()
        for file in files:
            if file:
                directories.add(Path(file).parent)
        return list(directories)
    except subprocess.CalledProcessError:
        return []

def cmd_start(args):
    """Start new session"""
    if not check_session_initialized():
        return 1

    # Checkout or create branch
    try:
        subprocess.run(["git", "checkout", args.branch], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        # Branch doesn't exist, create it
        try:
            subprocess.run(["git", "checkout", "-b", args.branch], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create branch: {e}")
            return 1

    # Parse objectives (can be comma-separated)
    objectives = []
    if args.objective:
        objectives = [obj.strip() for obj in args.objective.split(',')]

    # Determine mode
    mode = "tdd" if args.tdd else "normal"

    if INTEGRATION_AVAILABLE:
        # Use integrated session start
        integration = SessionIntegration()
        brief = integration.start_session(args.branch, objectives, mode)
        print(brief)
    else:
        # Fallback: Basic session start
        print(f"🚀 SESSION STARTED")
        print("=" * 60)
        print(f"Branch: {args.branch}")
        print(f"Mode: {mode.upper()}")
        if objectives:
            print("\n📋 OBJECTIVES:")
            for i, obj in enumerate(objectives, 1):
                print(f"  {i}. {obj}")
        print("\n" + "=" * 60)

    return 0

def cmd_resume(args):
    """Resume existing session"""
    if not check_session_initialized():
        return 1

    # Get branch to resume
    branch = args.branch if args.branch else get_current_branch()
    if not branch:
        print("❌ Not in a git repository")
        return 1

    # Checkout branch if specified
    if args.branch:
        try:
            subprocess.run(["git", "checkout", branch], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to checkout branch: {e}")
            return 1

    if INTEGRATION_AVAILABLE:
        # Load session state from integration
        integration = CCMPIntegration()
        session_state = integration.get_state("session-management")

        if session_state and session_state.get("active"):
            # Resume with full context
            session_int = SessionIntegration()
            brief = session_int.start_session(
                branch,
                session_state.get("objectives", []),
                session_state.get("mode", "normal")
            )
            print(brief)
        else:
            print(f"⚠️  No active session found for {branch}")
            print("Start a new session with: python session.py start <branch> --objective \"...\"")
    else:
        print(f"Resuming session on branch: {branch}")

    return 0

def cmd_checkpoint(args):
    """Create checkpoint"""
    if not check_session_initialized():
        return 1

    label = args.label or "checkpoint"

    if INTEGRATION_AVAILABLE:
        # Get changed directories for context health check
        changed_dirs = get_changed_directories()

        # Use integrated checkpoint with context health
        session_int = SessionIntegration()
        checkpoint_msg = session_int.checkpoint(label, changed_dirs)
        print(checkpoint_msg)

        # If TDD mode, update TDD state
        if is_tdd_mode():
            if args.tdd_phase:
                integration = CCMPIntegration()
                tdd_state = integration.get_state("tdd-workflow") or {}
                cycles = tdd_state.get("cycles_today", 0)

                if args.tdd_phase == "GREEN":
                    cycles += 1

                integration.update_state("tdd-workflow", {
                    "active": True,
                    "cycles_today": cycles,
                    "current_phase": args.tdd_phase,
                    "discipline_score": 100  # Would calculate based on violations
                })
                print(f"\n🧪 TDD: {args.tdd_phase} phase checkpoint created")
                if args.tdd_phase == "GREEN":
                    print(f"   Cycles completed today: {cycles}")
    else:
        print(f"✅ Checkpoint created: {label}")

    # Create git commit if there are changes
    try:
        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )
        if result.returncode != 0:  # There are staged changes
            commit_msg = args.message or f"checkpoint: {label}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            print(f"📝 Git commit created")
    except subprocess.CalledProcessError:
        pass  # No changes to commit

    return 0

def cmd_end(args):
    """End session"""
    if not check_session_initialized():
        return 1

    if INTEGRATION_AVAILABLE:
        # Use integrated session end with handoff
        session_int = SessionIntegration()
        handoff = session_int.end_session(generate_handoff=args.handoff)
        print(handoff)
    else:
        print("Session ended.")

    # Optional: merge to target branch
    if args.merge_to:
        try:
            current_branch = get_current_branch()
            subprocess.run(["git", "checkout", args.merge_to], check=True)
            subprocess.run(["git", "merge", current_branch], check=True)
            print(f"\n✅ Merged to {args.merge_to}")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Merge failed: {e}")
            return 1

    return 0

def cmd_status(args):
    """Show session status"""
    if not check_session_initialized():
        return 1

    branch = get_current_branch()
    print("📊 Session Status")
    print("=" * 60)
    print(f"Branch: {branch}")

    if INTEGRATION_AVAILABLE:
        integration = CCMPIntegration()
        session_state = integration.get_state("session-management")

        if session_state and session_state.get("active"):
            print(f"Status: ✅ Active")
            print(f"Mode: {session_state.get('mode', 'normal').upper()}")

            # Show objectives
            objectives = session_state.get("objectives", [])
            if objectives:
                print("\n📋 OBJECTIVES:")
                for i, obj in enumerate(objectives, 1):
                    print(f"  {i}. {obj}")

            # Show TDD metrics if in TDD mode
            if is_tdd_mode():
                tdd_state = integration.get_state("tdd-workflow")
                if tdd_state:
                    print("\n🧪 TDD METRICS:")
                    print(f"  Cycles today: {tdd_state.get('cycles_today', 0)}")
                    print(f"  Current phase: {tdd_state.get('current_phase', 'N/A')}")
                    print(f"  Discipline score: {tdd_state.get('discipline_score', 100)}/100")

            # Show context health
            context_state = integration.get_state("claude-context-manager")
            if context_state:
                health_score = context_state.get("health_score")
                if health_score is not None:
                    print("\n🏥 CONTEXT HEALTH:")
                    print(f"  Overall score: {health_score}/100")
                    critical = context_state.get("critical_files", [])
                    if critical:
                        print(f"  ⚠️  {len(critical)} files need attention")
        else:
            print("Status: ⚪ No active session")
            print("Start a session with: python session.py start <branch> --objective \"...\"")
    else:
        print("Status: ⚠️  Integration not available")

    print("=" * 60)
    return 0

def cmd_history(args):
    """Show session history"""
    if not check_session_initialized():
        return 1
    
    print(f"Showing last {args.count} sessions...")
    
    # Implementation would:
    # 1. Load archived sessions
    # 2. Display timeline
    # 3. Show metrics if requested
    # 4. Calculate trends
    
    return 0

def cmd_objectives(args):
    """Manage objectives"""
    if not check_session_initialized():
        return 1
    
    if args.action == "add":
        print(f"Adding objective: {args.text}")
    elif args.action == "complete":
        print(f"Completing objective: {args.id}")
    elif args.action == "list":
        print("Current Objectives:")
        # List objectives
    
    return 0

def cmd_blockers(args):
    """Manage blockers"""
    if not check_session_initialized():
        return 1
    
    if args.action == "add":
        print(f"Adding blocker: {args.text}")
    elif args.action == "resolve":
        print(f"Resolving blocker: {args.id}")
    elif args.action == "list":
        print("Active Blockers:")
        # List blockers
    
    return 0

def cmd_decisions(args):
    """Log decisions"""
    if not check_session_initialized():
        return 1
    
    if args.action == "add":
        print(f"Recording decision: {args.text}")
        if args.rationale:
            print(f"Rationale: {args.rationale}")
    elif args.action == "list":
        print("Decisions:")
        # List decisions
    
    return 0

def main():
    parser = argparse.ArgumentParser(description="Session Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # start command
    start_parser = subparsers.add_parser("start", help="Start new session")
    start_parser.add_argument("branch", help="Branch name")
    start_parser.add_argument("--objective", help="Session objective (comma-separated for multiple)")
    start_parser.add_argument("--tdd", action="store_true", help="Enable TDD mode")
    start_parser.add_argument("--resume", action="store_true", help="Resume if exists")
    start_parser.set_defaults(func=cmd_start)
    
    # resume command
    resume_parser = subparsers.add_parser("resume", help="Resume session")
    resume_parser.add_argument("branch", nargs="?", help="Branch to resume")
    resume_parser.set_defaults(func=cmd_resume)
    
    # checkpoint command
    checkpoint_parser = subparsers.add_parser("checkpoint", help="Create checkpoint")
    checkpoint_parser.add_argument("--label", help="Checkpoint label")
    checkpoint_parser.add_argument("--message", help="Commit message")
    checkpoint_parser.add_argument("--decision", help="Record decision")
    checkpoint_parser.add_argument("--tdd-phase", choices=["RED", "GREEN", "REFACTOR"], help="TDD phase for this checkpoint")
    checkpoint_parser.set_defaults(func=cmd_checkpoint)
    
    # end command
    end_parser = subparsers.add_parser("end", help="End session")
    end_parser.add_argument("--handoff", action="store_true", default=True, help="Generate handoff")
    end_parser.add_argument("--merge-to", help="Merge to branch")
    end_parser.set_defaults(func=cmd_end)
    
    # status command
    status_parser = subparsers.add_parser("status", help="Show status")
    status_parser.add_argument("--verbose", action="store_true", help="Verbose output")
    status_parser.set_defaults(func=cmd_status)
    
    # history command
    history_parser = subparsers.add_parser("history", help="Show history")
    history_parser.add_argument("--count", type=int, default=10, help="Number of sessions")
    history_parser.add_argument("--metrics", action="store_true", help="Include metrics")
    history_parser.set_defaults(func=cmd_history)
    
    # objectives command
    objectives_parser = subparsers.add_parser("objectives", help="Manage objectives")
    objectives_parser.add_argument("action", choices=["add", "complete", "list"])
    objectives_parser.add_argument("text", nargs="?", help="Objective text")
    objectives_parser.add_argument("--id", help="Objective ID")
    objectives_parser.set_defaults(func=cmd_objectives)
    
    # blockers command
    blockers_parser = subparsers.add_parser("blockers", help="Manage blockers")
    blockers_parser.add_argument("action", choices=["add", "resolve", "list"])
    blockers_parser.add_argument("text", nargs="?", help="Blocker description")
    blockers_parser.add_argument("--id", help="Blocker ID")
    blockers_parser.set_defaults(func=cmd_blockers)
    
    # decisions command
    decisions_parser = subparsers.add_parser("decisions", help="Log decisions")
    decisions_parser.add_argument("action", choices=["add", "list"])
    decisions_parser.add_argument("text", nargs="?", help="Decision text")
    decisions_parser.add_argument("--rationale", help="Decision rationale")
    decisions_parser.set_defaults(func=cmd_decisions)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
