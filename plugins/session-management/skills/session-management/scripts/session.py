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
    from tdd_analyzer import TDDAnalyzer
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    print("⚠️  Integration libraries not found. Running in standalone mode.")

def check_session_initialized():
    """Check if session management is initialized"""
    # Check for either .session or .sessions directory
    if not (Path(".session").exists() or Path(".sessions").exists()):
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

    # Generate project status report
    print("📊 Generating project status report...\n")

    # Import from project-status-report plugin
    import json
    from datetime import datetime

    # Add project-status-report to path
    report_plugin_path = Path(__file__).parents[5] / "plugins" / "project-status-report" / "skills" / "project-status-report" / "scripts"
    if report_plugin_path not in sys.path:
        sys.path.insert(0, str(report_plugin_path))

    try:
        from report import ReportGenerator

        generator = ReportGenerator()
        report = generator.generate()
        print(report)
        print("\n" + "=" * 60 + "\n")
    except ImportError:
        print("⚠️  project-status-report plugin not found, skipping report\n")

    # Handle branch selection
    branch = args.branch

    # Only present interactive prompts if branch not provided
    if not branch:
        print("What would you like to work on?")
        print()
        print("1. Resume existing work (if available)")
        print("2. Start new work")
        print("3. Address health issues first")
        print()

        choice = input("Choice [1/2/3]: ")

        if choice == "1":
            # Load branch from last session
            state_file = Path(".sessions") / "state.json"
            last_branch = None
            if state_file.exists():
                try:
                    with open(state_file) as f:
                        last_state = json.load(f)
                        last_branch = last_state.get("branch")
                except (json.JSONDecodeError, IOError):
                    pass

            if last_branch:
                print(f"\nLast session was on branch: {last_branch}")
                resume_choice = input(f"Resume '{last_branch}'? [Y/n]: ").strip().lower()
                if resume_choice in ['', 'y', 'yes']:
                    branch = last_branch
                else:
                    branch = input("Enter branch name to resume: ")
            else:
                print("\nNo previous session found.")
                branch = input("Enter branch name to resume: ")
        else:
            branch = input("Enter new branch name: ")

    # Checkout or create branch
    try:
        subprocess.run(["git", "checkout", branch], check=True, capture_output=True)
        print(f"✅ Switched to branch: {branch}")
    except subprocess.CalledProcessError:
        # Branch doesn't exist, create it
        try:
            subprocess.run(["git", "checkout", "-b", branch], check=True, capture_output=True)
            print(f"✅ Created new branch: {branch}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create branch: {e}")
            return 1

    # Parse objectives
    objectives = []
    if args.objective:
        objectives = [obj.strip() for obj in args.objective.split(',')]
    else:
        print("\nEnter session objectives (comma-separated):")
        obj_input = input("> ")
        if obj_input:
            objectives = [obj.strip() for obj in obj_input.split(',')]

    # Save session state
    mode = "tdd" if args.tdd else "normal"
    state = {
        "branch": branch,
        "objectives": objectives,
        "started_at": datetime.now().isoformat(),
        "mode": mode
    }

    state_file = Path(".sessions") / "state.json"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Update .ccmp/state.json if available
    ccmp_state_file = Path(".ccmp") / "state.json"
    if ccmp_state_file.parent.exists():
        try:
            if ccmp_state_file.exists():
                with open(ccmp_state_file) as f:
                    ccmp_state = json.load(f)
            else:
                ccmp_state = {}

            ccmp_state["session-management"] = {
                "active": True,
                "branch": branch,
                "objectives": objectives,
                "mode": state["mode"]
            }

            with open(ccmp_state_file, 'w') as f:
                json.dump(ccmp_state, f, indent=2)
        except (json.JSONDecodeError, IOError):
            pass

    # Display session ready message
    print("\n" + "=" * 60)
    print("🚀 SESSION READY")
    print("=" * 60)
    print(f"Branch: {branch}")
    print(f"Mode: {state['mode'].upper()}")
    if objectives:
        print("\n📋 OBJECTIVES:")
        for i, obj in enumerate(objectives, 1):
            print(f"  {i}. {obj}")
    print("=" * 60)

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

    # Use new CheckpointManager
    from checkpoint import CheckpointManager

    manager = CheckpointManager()
    label = args.label or "checkpoint"
    notes = args.notes if hasattr(args, 'notes') else None

    checkpoint = manager.generate_checkpoint(
        notes=notes,
        label=label
    )

    print(checkpoint)
    print(f"\n✅ Checkpoint saved")

    # Git commit handling (if requested)
    if hasattr(args, 'commit') and args.commit:
        # Check for uncommitted changes
        try:
            result = subprocess.run(
                ["git", "diff", "--quiet"],
                capture_output=True
            )
            if result.returncode != 0:  # There are changes
                # Stage all changes
                subprocess.run(["git", "add", "."], check=True)

                # Generate commit message
                commit_msg = args.message if hasattr(args, 'message') and args.message else None

                # If no custom message, use git-commit skill to analyze and suggest
                if not commit_msg:
                    try:
                        # Run analyze-diff.py from git-commit plugin
                        analyzer_script = repo_root / "plugins" / "git-commit" / "skills" / "git-commit" / "scripts" / "analyze-diff.py"

                        if analyzer_script.exists():
                            result = subprocess.run(
                                ["python3", str(analyzer_script), "--json"],
                                capture_output=True,
                                text=True,
                                check=True
                            )

                            analysis = json.loads(result.stdout)

                            if analysis and 'error' not in analysis:
                                # Build commit message from analysis
                                msg_type = analysis['type']
                                scope = f"({analysis['scope']})" if analysis['scope'] else ""
                                breaking = "!" if analysis['breaking'] else ""
                                desc = analysis['description']

                                commit_msg = f"{msg_type}{scope}{breaking}: {desc}"

                                # Add notes as body if provided
                                if notes:
                                    commit_msg = f"{commit_msg}\n\n{notes}"

                                print(f"\n📊 Analyzed changes: {msg_type} ({analysis['confidence']:.0%} confidence)")
                                print(f"📝 Suggested commit:\n   {commit_msg.split(chr(10))[0]}")
                            else:
                                # Fallback to checkpoint label
                                commit_msg = f"checkpoint: {label}"
                                if notes:
                                    commit_msg = f"{commit_msg}\n\n{notes}"
                        else:
                            # git-commit skill not found, use simple message
                            commit_msg = f"checkpoint: {label}"
                            if notes:
                                commit_msg = f"{commit_msg}\n\n{notes}"
                    except Exception as e:
                        # On any error, fall back to simple message
                        print(f"⚠️  Commit analysis failed ({e}), using simple message")
                        commit_msg = f"checkpoint: {label}"
                        if notes:
                            commit_msg = f"{commit_msg}\n\n{notes}"
                else:
                    # Custom message provided, add notes if present
                    if notes:
                        commit_msg = f"{commit_msg}\n\n{notes}"

                # Create commit
                subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                print("📝 Git commit created")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git commit failed: {e}")

    # Legacy integration support
    if INTEGRATION_AVAILABLE and is_tdd_mode() and hasattr(args, 'tdd_phase') and args.tdd_phase:
        integration = CCMPIntegration()
        tdd_state = integration.get_state("tdd-workflow") or {}

        if args.tdd_phase == "GREEN":
            cycles = tdd_state.get("cycles_today", 0) + 1
            integration.update_state("tdd-workflow", {
                "active": True,
                "cycles_today": cycles,
                "current_phase": "GREEN",
                "discipline_score": 100
            })
            print(f"\n🎯 TDD Cycles completed today: {cycles}")
        else:
            integration.update_state("tdd-workflow", {
                "active": True,
                "cycles_today": tdd_state.get("cycles_today", 0),
                "current_phase": args.tdd_phase,
                "discipline_score": 100
            })
            print(f"\n🧪 TDD: {args.tdd_phase} phase checkpoint created")

    return 0

def cmd_end(args):
    """End session"""
    if not check_session_initialized():
        return 1

    # Gather session notes - use args if provided, otherwise prompt
    accomplished = args.accomplished if hasattr(args, 'accomplished') and args.accomplished else None
    decisions = args.decisions if hasattr(args, 'decisions') and args.decisions else None
    remember = args.remember if hasattr(args, 'remember') and args.remember else None

    # Only prompt if not provided via arguments
    if not accomplished or not decisions or not remember:
        print("\nSession Summary Notes:")
        if not accomplished:
            print("\nWhat did you accomplish?")
            accomplished = input("> ")
        if not decisions:
            print("\nKey decisions made?")
            decisions = input("> ")
        if not remember:
            print("\nWhat to remember for next session?")
            remember = input("> ")

    session_notes = f"""**Accomplished**: {accomplished}

**Decisions**: {decisions}

**Remember**: {remember}
"""

    # Generate handoff
    from handoff import HandoffGenerator

    generator = HandoffGenerator()
    handoff = generator.generate_handoff(session_notes=session_notes)

    print("\n" + handoff)
    print(f"\n✅ Session ended. Handoff generated.")

    # Git push handling
    should_push = False
    if hasattr(args, 'no_push') and args.no_push:
        should_push = False
    elif hasattr(args, 'push') and args.push:
        should_push = True
    else:
        # Default behavior: ask user
        try:
            # Check for commits to push
            result = subprocess.run(
                ["git", "log", "@{u}..", "--oneline"],
                capture_output=True,
                text=True,
                check=True
            )
            commits = result.stdout.strip().split("\n")

            if commits and commits[0]:
                print(f"\nCommits to push: {len(commits)}")
                for commit in commits[:5]:
                    print(f"  - {commit}")

                response = input(f"\nPush {len(commits)} commits to remote? [Y/n]: ")
                should_push = response.lower() != 'n'
        except subprocess.CalledProcessError:
            print("⚠️  No commits to push")
            should_push = False

    # Execute push if decided
    if should_push:
        try:
            subprocess.run(["git", "push"], check=True)
            print("📤 Pushed to remote")
        except subprocess.CalledProcessError:
            print("⚠️  Git push failed")

    # Optional: merge to target branch
    if hasattr(args, 'merge_to') and args.merge_to:
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

def cmd_analyze(args):
    """Analyze session metrics"""
    if not check_session_initialized():
        return 1

    if INTEGRATION_AVAILABLE and is_tdd_mode():
        # Run TDD analysis
        analyzer = TDDAnalyzer()

        print("🔍 Analyzing TDD discipline...")
        print()

        # Analyze commits
        commit_analysis = analyzer.analyze_session_commits()
        print(analyzer.generate_violation_report(commit_analysis))

        # Analyze cycle timing
        cycle_analysis = analyzer.analyze_tdd_cycle_timing()
        if cycle_analysis["total_cycles"] > 0:
            print("⏱️  TDD Cycle Timing:")
            print(f"  • Total cycles: {cycle_analysis['total_cycles']}")
            print(f"  • Average cycle time: {cycle_analysis['average_cycle_time']:.1f} minutes")
            print(f"  • Fastest cycle: {cycle_analysis['fastest_cycle']:.1f} minutes")
            print(f"  • Slowest cycle: {cycle_analysis['slowest_cycle']:.1f} minutes")
            print()
    else:
        print("Session Analysis")
        print("=" * 50)
        print("Analysis features available in TDD mode with integration enabled")

    return 0

def main():
    parser = argparse.ArgumentParser(description="Session Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # start command
    start_parser = subparsers.add_parser("start", help="Start new session")
    start_parser.add_argument("branch", nargs="?", help="Branch name (optional, will prompt if not provided)")
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
    checkpoint_parser.add_argument("--notes", help="Checkpoint notes")
    checkpoint_parser.add_argument("--commit", action="store_true", help="Create git commit")
    checkpoint_parser.add_argument("--message", help="Commit message")
    checkpoint_parser.add_argument("--decision", help="Record decision")
    checkpoint_parser.add_argument("--tdd-phase", choices=["RED", "GREEN", "REFACTOR"], help="TDD phase for this checkpoint")
    checkpoint_parser.set_defaults(func=cmd_checkpoint)
    
    # end command
    end_parser = subparsers.add_parser("end", help="End session")
    end_parser.add_argument("--handoff", action="store_true", default=True, help="Generate handoff")
    end_parser.add_argument("--push", action="store_true", help="Push commits to remote")
    end_parser.add_argument("--no-push", action="store_true", help="Don't push commits to remote")
    end_parser.add_argument("--accomplished", help="What was accomplished in this session")
    end_parser.add_argument("--decisions", help="Key decisions made")
    end_parser.add_argument("--remember", help="What to remember for next session")
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

    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze session metrics")
    analyze_parser.set_defaults(func=cmd_analyze)

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
