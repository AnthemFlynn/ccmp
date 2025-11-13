import pytest
from health_check import HealthChecker

def test_check_tests_basic():
    """Test that we can check test status"""
    checker = HealthChecker()
    result = checker.check_tests()
    assert "status" in result
    assert result["status"] in ["pass", "fail", "unknown"]

def test_generate_report():
    """Test health report generation"""
    checker = HealthChecker()
    report = checker.generate_report()
    assert isinstance(report, str)
    assert "Health Indicators" in report
