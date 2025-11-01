#!/usr/bin/env python3
"""
CCMP Integration Library

Provides unified API for Claude Code plugins to detect and interact with each other.

Usage:
    from lib.ccmp_integration import CCMPIntegration

    integration = CCMPIntegration()

    # Check if plugin is active
    if integration.is_active("session-management"):
        session = integration.get_state("session-management")

    # Update own state
    integration.update_state("tdd-workflow", {
        "cycles_today": 5,
        "active": True
    })
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class CCMPIntegration:
    """Integration API for CCMP plugins."""

    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize integration API.

        Args:
            repo_path: Path to repository root. If None, searches upward for .ccmp/
        """
        self.repo_path = self._find_repo_root(repo_path)
        self.state_file = self.repo_path / ".ccmp" / "state.json"
        self._ensure_state_file()

    def _find_repo_root(self, start_path: Optional[str] = None) -> Path:
        """Find repository root by looking for .ccmp/ directory."""
        current = Path(start_path or os.getcwd()).resolve()

        # Search upward for .ccmp directory
        while current != current.parent:
            if (current / ".ccmp").exists():
                return current
            current = current.parent

        # Not found, use current directory
        return Path(start_path or os.getcwd()).resolve()

    def _ensure_state_file(self):
        """Ensure state file exists with default structure."""
        if not self.state_file.exists():
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self._write_state({
                "version": "1.0.0",
                "last_updated": None,
                "plugins": {}
            })

    def _read_state(self) -> Dict[str, Any]:
        """Read current state from file."""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "version": "1.0.0",
                "last_updated": None,
                "plugins": {}
            }

    def _write_state(self, state: Dict[str, Any]):
        """Write state to file."""
        state["last_updated"] = datetime.utcnow().isoformat() + "Z"
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
            f.write('\n')

    def is_active(self, plugin_name: str) -> bool:
        """
        Check if a plugin is currently active.

        Args:
            plugin_name: Name of plugin (e.g., "session-management")

        Returns:
            True if plugin is active, False otherwise
        """
        state = self._read_state()
        plugin_state = state.get("plugins", {}).get(plugin_name, {})
        return plugin_state.get("active", False)

    def is_installed(self, plugin_name: str) -> bool:
        """
        Check if a plugin is installed.

        Args:
            plugin_name: Name of plugin

        Returns:
            True if plugin is installed, False otherwise
        """
        state = self._read_state()
        plugin_state = state.get("plugins", {}).get(plugin_name, {})
        return plugin_state.get("installed", False)

    def get_state(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get current state for a plugin.

        Args:
            plugin_name: Name of plugin

        Returns:
            Plugin state dictionary, or empty dict if not found
        """
        state = self._read_state()
        return state.get("plugins", {}).get(plugin_name, {})

    def update_state(self, plugin_name: str, updates: Dict[str, Any]):
        """
        Update state for a plugin.

        Args:
            plugin_name: Name of plugin
            updates: Dictionary of updates to merge into plugin state
        """
        state = self._read_state()

        if "plugins" not in state:
            state["plugins"] = {}

        if plugin_name not in state["plugins"]:
            state["plugins"][plugin_name] = {}

        state["plugins"][plugin_name].update(updates)
        self._write_state(state)

    def set_active(self, plugin_name: str, active: bool = True):
        """
        Mark a plugin as active or inactive.

        Args:
            plugin_name: Name of plugin
            active: True to activate, False to deactivate
        """
        self.update_state(plugin_name, {"active": active})

    def get_all_active(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active plugins and their states.

        Returns:
            Dictionary mapping plugin names to their states
        """
        state = self._read_state()
        plugins = state.get("plugins", {})
        return {
            name: plugin_state
            for name, plugin_state in plugins.items()
            if plugin_state.get("active", False)
        }

    def clear_state(self, plugin_name: str):
        """
        Clear state for a plugin.

        Args:
            plugin_name: Name of plugin
        """
        state = self._read_state()
        if "plugins" in state and plugin_name in state["plugins"]:
            state["plugins"][plugin_name] = {
                "installed": True,
                "active": False
            }
            self._write_state(state)


# Convenience functions for common operations

def is_session_active() -> bool:
    """Check if a session-management session is active."""
    integration = CCMPIntegration()
    return integration.is_active("session-management")


def get_session_info() -> Optional[Dict[str, Any]]:
    """Get current session information, or None if no session active."""
    integration = CCMPIntegration()
    if not integration.is_active("session-management"):
        return None
    return integration.get_state("session-management")


def is_tdd_mode() -> bool:
    """Check if current session is in TDD mode."""
    session = get_session_info()
    if not session:
        return False
    return session.get("mode") == "tdd"


def get_context_health() -> Optional[Dict[str, Any]]:
    """Get context health information from claude-context-manager."""
    integration = CCMPIntegration()
    context_state = integration.get_state("claude-context-manager")
    if not context_state:
        return None
    return {
        "health_score": context_state.get("health_score"),
        "last_scan": context_state.get("last_scan"),
        "critical_files": context_state.get("critical_files", [])
    }


if __name__ == "__main__":
    # Test the integration API
    integration = CCMPIntegration()

    print("CCMP Integration API Test")
    print("=" * 50)

    # Check active plugins
    active = integration.get_all_active()
    print(f"\nActive plugins: {len(active)}")
    for name, state in active.items():
        print(f"  - {name}: {state}")

    # Test session detection
    if is_session_active():
        session = get_session_info()
        print(f"\nSession active: {session.get('branch')}")
        print(f"Mode: {session.get('mode')}")
    else:
        print("\nNo active session")

    # Test context health
    health = get_context_health()
    if health:
        print(f"\nContext health: {health['health_score']}/100")
    else:
        print("\nNo context health data")
