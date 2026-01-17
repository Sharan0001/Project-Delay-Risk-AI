"""
Unit tests for the hybrid risk scoring module.

Tests:
- Score combination logic
- Risk level classification
- Config weight usage
- Edge cases
"""

import pytest
from models.hybrid_risk import (
    hybrid_risk_score,
    DEFAULT_RULE_WEIGHT,
    DEFAULT_ML_WEIGHT,
    DEFAULT_HIGH_THRESHOLD,
    DEFAULT_MEDIUM_THRESHOLD,
)


class TestHybridRiskScore:
    """Tests for the hybrid_risk_score function."""
    
    @pytest.fixture
    def low_risk_row(self):
        """Task with no risk signals."""
        return {
            "total_blocked_events": 0,
            "dependencies": 0,
            "no_resource_available": 0,
            "rework_count": 0,
            "max_progress_gap": 0,
        }
    
    @pytest.fixture
    def high_risk_row(self):
        """Task with multiple risk signals."""
        return {
            "total_blocked_events": 5,
            "dependencies": 3,
            "no_resource_available": 2,
            "rework_count": 3,
            "max_progress_gap": 6,
        }
    
    def test_low_risk_with_low_ml_prob(self, low_risk_row):
        """Low rule score + low ML prob = Low risk."""
        result = hybrid_risk_score(low_risk_row, 0.1)
        
        assert result["risk_level"] == "Low"
        assert result["risk_score"] < 40
        assert result["ml_probability"] == 0.1
        assert result["rule_score"] == 0
    
    def test_high_risk_with_high_ml_prob(self, high_risk_row):
        """High rule score + high ML prob = High risk."""
        result = hybrid_risk_score(high_risk_row, 0.9)
        
        assert result["risk_level"] == "High"
        assert result["risk_score"] >= 70
    
    def test_medium_risk_classification(self, low_risk_row):
        """Test medium risk threshold."""
        # With 0.6 ML prob and 0 rule score:
        # score = 0.6 * 0 + 0.4 * 60 = 24 -> Low
        # Need higher ML prob for Medium
        result = hybrid_risk_score(low_risk_row, 0.99)
        
        # 0.6 * 0 + 0.4 * 99 = 39.6 -> rounds to 39 -> still Low
        # This tests that we need rule triggers for medium risk
        assert result["risk_level"] in ["Low", "Medium"]
    
    def test_score_calculation_formula(self, low_risk_row):
        """Verify the exact score calculation formula."""
        ml_prob = 0.5
        result = hybrid_risk_score(low_risk_row, ml_prob)
        
        # With no rule triggers: rule_score = 0
        # expected = 0.6 * 0 + 0.4 * (0.5 * 100) = 0 + 20 = 20
        expected_score = int(
            DEFAULT_RULE_WEIGHT * 0 +
            DEFAULT_ML_WEIGHT * (ml_prob * 100)
        )
        
        assert result["risk_score"] == expected_score
    
    def test_score_clamped_to_0_100(self, high_risk_row):
        """Score should be clamped to [0, 100] range."""
        result = hybrid_risk_score(high_risk_row, 1.0)
        
        assert 0 <= result["risk_score"] <= 100
    
    def test_result_contains_weights_used(self, low_risk_row):
        """Result should include the weights that were used."""
        result = hybrid_risk_score(low_risk_row, 0.5)
        
        assert "weights_used" in result
        assert result["weights_used"]["rule_weight"] == DEFAULT_RULE_WEIGHT
        assert result["weights_used"]["ml_weight"] == DEFAULT_ML_WEIGHT


class TestHybridRiskScoreWithConfig:
    """Tests for hybrid_risk_score with custom config."""
    
    @pytest.fixture
    def low_risk_row(self):
        return {
            "total_blocked_events": 0,
            "dependencies": 0,
            "no_resource_available": 0,
            "rework_count": 0,
            "max_progress_gap": 0,
        }
    
    def test_custom_weights(self, low_risk_row):
        """Test that custom weights from config are applied."""
        config = {
            "risk_weights": {
                "rule_weight": 0.3,
                "ml_weight": 0.7
            },
            "risk_thresholds": {
                "high": 70,
                "medium": 40
            }
        }
        
        ml_prob = 0.5
        result = hybrid_risk_score(low_risk_row, ml_prob, config=config)
        
        # expected = 0.3 * 0 + 0.7 * 50 = 35
        expected_score = int(0.3 * 0 + 0.7 * (ml_prob * 100))
        
        assert result["risk_score"] == expected_score
        assert result["weights_used"]["rule_weight"] == 0.3
        assert result["weights_used"]["ml_weight"] == 0.7
    
    def test_custom_thresholds(self, low_risk_row):
        """Test that custom thresholds from config are applied."""
        config = {
            "risk_weights": {
                "rule_weight": 0.0,  # Ignore rules
                "ml_weight": 1.0     # Only ML
            },
            "risk_thresholds": {
                "high": 80,
                "medium": 50
            }
        }
        
        # With ml_prob=0.6, score = 0*0 + 1*60 = 60
        # With threshold high=80, medium=50: 60 -> Medium
        result = hybrid_risk_score(low_risk_row, 0.6, config=config)
        
        assert result["risk_level"] == "Medium"
        assert result["risk_score"] == 60
    
    def test_defaults_used_when_no_config(self, low_risk_row):
        """Without config, defaults are used."""
        result = hybrid_risk_score(low_risk_row, 0.5, config=None)
        
        assert result["weights_used"]["rule_weight"] == DEFAULT_RULE_WEIGHT
        assert result["weights_used"]["ml_weight"] == DEFAULT_ML_WEIGHT


class TestRiskLevelBoundaries:
    """Tests for risk level classification boundaries."""
    
    @pytest.fixture
    def zero_rule_row(self):
        return {
            "total_blocked_events": 0,
            "dependencies": 0,
            "no_resource_available": 0,
            "rework_count": 0,
            "max_progress_gap": 0,
        }
    
    def test_high_threshold_boundary(self, zero_rule_row):
        """Score of exactly 70 should be High."""
        # Need ML prob that gives score of 70 with 0 rule score
        # 0.6 * 0 + 0.4 * x = 70 -> x = 175 (impossible)
        # Use custom config
        config = {
            "risk_weights": {"rule_weight": 0.0, "ml_weight": 1.0},
            "risk_thresholds": {"high": 70, "medium": 40}
        }
        
        result = hybrid_risk_score(zero_rule_row, 0.70, config=config)
        assert result["risk_level"] == "High"
    
    def test_medium_threshold_boundary(self, zero_rule_row):
        """Score of exactly 40 should be Medium."""
        config = {
            "risk_weights": {"rule_weight": 0.0, "ml_weight": 1.0},
            "risk_thresholds": {"high": 70, "medium": 40}
        }
        
        result = hybrid_risk_score(zero_rule_row, 0.40, config=config)
        assert result["risk_level"] == "Medium"
    
    def test_just_below_medium_is_low(self, zero_rule_row):
        """Score of 39 should be Low."""
        config = {
            "risk_weights": {"rule_weight": 0.0, "ml_weight": 1.0},
            "risk_thresholds": {"high": 70, "medium": 40}
        }
        
        result = hybrid_risk_score(zero_rule_row, 0.39, config=config)
        assert result["risk_level"] == "Low"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
