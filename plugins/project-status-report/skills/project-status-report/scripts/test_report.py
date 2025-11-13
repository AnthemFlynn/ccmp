import pytest
from report import ReportGenerator

def test_generate_full_report():
    """Test generating complete project status report"""
    generator = ReportGenerator()
    report = generator.generate()

    assert isinstance(report, str)
    assert "Project Status Report" in report
    assert "Health Indicators" in report
    assert "Git Status" in report
    assert "Open Work Items" in report
