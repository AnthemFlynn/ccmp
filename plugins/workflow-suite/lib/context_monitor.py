#!/usr/bin/env python3
"""
Real-Time Context Monitoring

Monitors codebase for changes and automatically checks context health.
Can run as daemon or one-shot.

Usage:
    python context_monitor.py                    # One-shot check
    python context_monitor.py --watch            # Continuous monitoring
    python context_monitor.py --watch --interval 300  # Check every 5 minutes
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import subprocess

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

from ccmp_integration import CCMPIntegration, is_session_active
from context_loader import ContextLoader


class ContextMonitor:
    """Real-time context health monitor"""

    def __init__(self, repo_path: str = "."):
        """Initialize monitor"""
        self.repo_path = Path(repo_path).resolve()
        self.integration = CCMPIntegration(str(self.repo_path))
        self.loader = ContextLoader(str(self.repo_path))
        self.last_check: Dict[str, float] = {}

    def get_recently_changed_dirs(self, since_minutes: int = 60) -> List[Path]:
        """Get directories with recent changes"""
        try:
            # Get files changed in last N minutes
            result = subprocess.run(
                ["git", "diff", "--name-only", f"HEAD@{{{since_minutes} minutes ago}}", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )

            if result.returncode != 0:
                return []

            files = result.stdout.strip().split('\n')
            directories = set()
            for file in files:
                if file:
                    directories.add(Path(file).parent)

            return list(directories)
        except Exception:
            return []

    def check_context_health(self, directories: List[Path] = None) -> Dict:
        """Check context health for directories"""
        if directories is None:
            # Check all context files
            context_files = self.loader.find_all_context_files()
            directories = [f.parent for f in context_files]

        return self.loader.check_context_health(directories)

    def calculate_overall_health(self, health_report: Dict) -> int:
        """Calculate overall health score 0-100"""
        healthy = len(health_report.get("healthy", []))
        stale = len(health_report.get("stale", []))
        missing = len(health_report.get("missing", []))

        total = healthy + stale + missing
        if total == 0:
            return 100

        # Scoring: healthy=full points, stale=half points, missing=0 points
        score = (healthy + (stale * 0.5)) / total * 100
        return int(score)

    def run_check(self, verbose: bool = False) -> Dict:
        """Run single health check"""
        if verbose:
            print(f"🔍 Checking context health at {datetime.now().strftime('%H:%M:%S')}")

        # Get recently changed directories
        changed_dirs = self.get_recently_changed_dirs(since_minutes=60)

        # Check all context health
        health_report = self.check_context_health()
        overall_score = self.calculate_overall_health(health_report)

        # Update integration state
        self.integration.update_state("claude-context-manager", {
            "health_score": overall_score,
            "last_scan": datetime.now().isoformat(),
            "critical_files": [str(item["path"]) for item in health_report.get("stale", []) if item.get("age_days", 0) > 30]
        })

        if verbose:
            print(f"   Overall health: {overall_score}/100")
            if health_report["stale"]:
                print(f"   ⚠️  {len(health_report['stale'])} stale contexts")
            if health_report["missing"]:
                print(f"   ℹ️  {len(health_report['missing'])} missing contexts")

            # Highlight recently changed directories
            if changed_dirs:
                print(f"\n📝 Recently changed directories:")
                for dir_path in changed_dirs:
                    # Check if this directory has stale context
                    is_stale = any(item["path"] == dir_path for item in health_report.get("stale", []))
                    is_missing = dir_path in health_report.get("missing", [])

                    if is_stale:
                        print(f"   ⚠️  {dir_path} (stale context)")
                    elif is_missing:
                        print(f"   ℹ️  {dir_path} (no context)")
                    else:
                        print(f"   ✅ {dir_path} (healthy)")

        return {
            "overall_score": overall_score,
            "health_report": health_report,
            "changed_dirs": changed_dirs
        }

    def watch(self, interval: int = 300, verbose: bool = True):
        """Watch for changes continuously"""
        print(f"👁️  Context monitor started (checking every {interval}s)")
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                result = self.run_check(verbose=verbose)

                # Alert if health score drops below threshold
                if result["overall_score"] < 70:
                    print(f"\n⚠️  WARNING: Context health below 70% ({result['overall_score']}/100)")
                    print("   Consider running context updates")

                # Alert if session active and context is stale
                if is_session_active():
                    session_state = self.integration.get_state("session-management")
                    if session_state and result["health_report"]["stale"]:
                        print(f"\n💡 Active session detected with stale context")
                        print("   Run checkpoints to get context health warnings")

                if verbose:
                    print(f"\n⏰ Next check in {interval}s...\n")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n✋ Monitor stopped")


def main():
    parser = argparse.ArgumentParser(description="Context Health Monitor")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring mode")
    parser.add_argument("--interval", type=int, default=300, help="Check interval in seconds (default: 300)")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    parser.add_argument("--repo", default=".", help="Repository path (default: current directory)")

    args = parser.parse_args()

    monitor = ContextMonitor(args.repo)

    if args.watch:
        # Continuous monitoring
        monitor.watch(interval=args.interval, verbose=not args.quiet)
    else:
        # One-shot check
        result = monitor.run_check(verbose=not args.quiet)

        if not args.quiet:
            print(f"\n📊 Overall Health: {result['overall_score']}/100")

        # Exit code based on health
        if result["overall_score"] < 50:
            sys.exit(2)  # Critical
        elif result["overall_score"] < 70:
            sys.exit(1)  # Warning
        else:
            sys.exit(0)  # Healthy


if __name__ == "__main__":
    main()
