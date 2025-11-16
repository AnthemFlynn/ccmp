"""Pytest configuration for project-status-report tests."""
import sys
from pathlib import Path

# Add the scripts directory to Python path so tests can import modules
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
