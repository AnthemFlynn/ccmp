import pytest
from git_analysis import GitAnalyzer

def test_get_current_branch():
    """Test that we can get current git branch"""
    analyzer = GitAnalyzer()
    branch = analyzer.get_current_branch()
    assert branch is not None
    assert isinstance(branch, str)
    assert len(branch) > 0

def test_get_uncommitted_changes():
    """Test detection of uncommitted changes"""
    analyzer = GitAnalyzer()
    changes = analyzer.get_uncommitted_changes()
    assert isinstance(changes, dict)
    assert "modified" in changes
    assert "untracked" in changes
    assert isinstance(changes["modified"], list)
    assert isinstance(changes["untracked"], list)

def test_get_active_branches():
    """Test listing active branches with recent activity"""
    analyzer = GitAnalyzer()
    branches = analyzer.get_active_branches(limit=5)
    assert isinstance(branches, list)
    assert len(branches) <= 5
    for branch in branches:
        assert "name" in branch
        assert "last_commit" in branch
        assert "last_activity" in branch
