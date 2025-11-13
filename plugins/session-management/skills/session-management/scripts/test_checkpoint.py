import pytest
from pathlib import Path
from checkpoint import CheckpointManager

def test_analyze_git_changes():
    """Test analyzing git diff for changes"""
    manager = CheckpointManager()
    changes = manager.analyze_git_changes()
    assert isinstance(changes, dict)
    assert "modified" in changes
    assert "added" in changes
    assert "deleted" in changes

def test_generate_checkpoint():
    """Test generating checkpoint document"""
    manager = CheckpointManager()
    checkpoint = manager.generate_checkpoint(notes="Test notes")
    assert isinstance(checkpoint, str)
    assert "Checkpoint:" in checkpoint
    assert "What Changed" in checkpoint
