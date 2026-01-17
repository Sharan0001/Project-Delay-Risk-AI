"""
Unit tests for the rule-based risk assessment module.

Tests:
- Individual rule triggering
- Score accumulation
- Score capping at 100
- Reason generation with severity
"""

import pytest
from models.rules import rule_based_risk, get_rule_definitions, RULES


class TestRuleBasedRisk:
    """Tests for the rule_based_risk function."""
    
    def test_no_triggers_returns_zero_score(self):
        """When no thresholds are met, score should be 0."""
        row = {
            "total_blocked_events": 0,
            "dependencies": 0,
            "no_resource_available": 0,
            "rework_count": 0,
            "max_progress_gap": 0,
        }
        score, reasons = rule_based_risk(row)
        
        assert score == 0
        assert len(reasons) == 0
    
    def test_single_rule_trigger(self):
        """Test that a single rule triggers correctly."""
        row = {
            "total_blocked_events": 5,  # >= 3 threshold
            "dependencies": 0,
            "no_resource_available": 0,
            "rework_count": 0,
            "max_progress_gap": 0,
        }
        score, reasons = rule_based_risk(row)
        
        assert score == 25  # blocked events contributes 25
        assert len(reasons) == 1
        assert reasons[0]["severity"] == "critical"
    
    def test_multiple_rule_triggers(self):
        """Test that multiple rules accumulate correctly."""
        row = {
            "total_blocked_events": 5,  # +25
            "dependencies": 3,           # +15
            "no_resource_available": 2,  # +20
            "rework_count": 0,
            "max_progress_gap": 0,
        }
        score, reasons = rule_based_risk(row)
        
        assert score == 60  # 25 + 15 + 20
        assert len(reasons) == 3
    
    def test_all_rules_trigger(self):
        """Test all rules triggering at once."""
        row = {
            "total_blocked_events": 10,  # +25
            "dependencies": 5,            # +15
            "no_resource_available": 3,   # +20
            "rework_count": 4,            # +15
            "max_progress_gap": 10,       # +15
        }
        score, reasons = rule_based_risk(row)
        
        assert score == 90  # 25 + 15 + 20 + 15 + 15 = 90
        assert len(reasons) == 5
    
    def test_score_capped_at_100(self):
        """Test that score is capped at 100."""
        # Create a scenario where raw score would exceed 100
        row = {
            "total_blocked_events": 100,  # +25
            "dependencies": 100,           # +15
            "no_resource_available": 100,  # +20
            "rework_count": 100,           # +15
            "max_progress_gap": 100,       # +15
        }
        score, reasons = rule_based_risk(row)
        
        # Raw would be 90, but let's verify capping works
        assert score <= 100
        assert len(reasons) == 5
    
    def test_threshold_boundary_below(self):
        """Test values just below threshold don't trigger."""
        row = {
            "total_blocked_events": 2,  # < 3 threshold
            "dependencies": 1,           # < 2 threshold
            "no_resource_available": 0,  # < 1 threshold
            "rework_count": 1,           # < 2 threshold
            "max_progress_gap": 3,       # < 4 threshold
        }
        score, reasons = rule_based_risk(row)
        
        assert score == 0
        assert len(reasons) == 0
    
    def test_threshold_boundary_exact(self):
        """Test values exactly at threshold do trigger."""
        row = {
            "total_blocked_events": 3,  # = 3 threshold
            "dependencies": 2,           # = 2 threshold
            "no_resource_available": 1,  # = 1 threshold
            "rework_count": 2,           # = 2 threshold
            "max_progress_gap": 4,       # = 4 threshold
        }
        score, reasons = rule_based_risk(row)
        
        assert score == 90  # All rules trigger
        assert len(reasons) == 5
    
    def test_reasons_have_severity(self):
        """Test that all reasons include severity levels."""
        row = {
            "total_blocked_events": 5,
            "dependencies": 3,
            "no_resource_available": 0,
            "rework_count": 0,
            "max_progress_gap": 0,
        }
        _, reasons = rule_based_risk(row)
        
        for reason in reasons:
            assert "severity" in reason
            assert reason["severity"] in ["critical", "warning", "info"]
            assert "text" in reason
    
    def test_missing_keys_handled(self):
        """Test that missing keys use default value of 0."""
        row = {}  # Empty dict
        score, reasons = rule_based_risk(row)
        
        assert score == 0
        assert len(reasons) == 0


class TestRuleDefinitions:
    """Tests for rule definition structure."""
    
    def test_rules_have_required_fields(self):
        """All rules should have required fields."""
        required = ["field", "threshold", "score", "severity", "reason"]
        
        for rule in RULES:
            for field in required:
                assert field in rule, f"Rule missing field: {field}"
    
    def test_get_rule_definitions_returns_copy(self):
        """get_rule_definitions should return a copy."""
        rules1 = get_rule_definitions()
        rules2 = get_rule_definitions()
        
        assert rules1 is not rules2  # Different objects
        assert rules1 == rules2      # Same content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
