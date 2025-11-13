import pytest
from handoff import HandoffGenerator

def test_generate_handoff():
    """Test generating session handoff document"""
    generator = HandoffGenerator()
    handoff = generator.generate_handoff(
        session_notes="Test session notes"
    )
    assert isinstance(handoff, str)
    assert "Session Handoff" in handoff
    assert "Test session notes" in handoff
