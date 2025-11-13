import pytest
from pathlib import Path
from work_items import WorkItemsScanner

def test_scan_code_markers():
    """Test scanning code for TODO/FIXME markers"""
    scanner = WorkItemsScanner()
    markers = scanner.scan_code_markers()
    assert isinstance(markers, dict)
    assert "todos" in markers
    assert "fixmes" in markers

def test_load_session_objectives():
    """Test loading objectives from session state"""
    scanner = WorkItemsScanner()
    objectives = scanner.load_session_objectives()
    # Should return list even if file doesn't exist
    assert isinstance(objectives, list)
