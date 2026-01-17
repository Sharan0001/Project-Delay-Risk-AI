"""
Unit Tests for What-If Analysis Module.

Tests scenario simulation and feature perturbation.
"""

import pytest
import pandas as pd

from decision_support.what_if import (
    simulate_what_if,
    get_available_scenarios,
    estimate_scenario_impact,
    SCENARIOS
)


class TestSimulateWhatIf:
    """Tests for the simulate_what_if function."""
    
    @pytest.fixture
    def sample_row(self):
        """Creates a sample task feature row."""
        return pd.Series({
            "task_id": "T1",
            "total_blocked_events": 5,
            "dependencies": 3,
            "no_resource_available": 2,
            "rework_count": 4,
            "max_progress_gap": 6,
            "external_block": 1,
            "random_disruption": 2,
        })
    
    def test_add_resource_reduces_resource_unavailable(self, sample_row):
        """Tests that add_resource scenario reduces no_resource_available."""
        result = simulate_what_if(sample_row, "add_resource")
        
        assert result["no_resource_available"] < sample_row["no_resource_available"]
        assert result["no_resource_available"] == 1  # 2 - 1

    def test_add_resource_reduces_total_blocked(self, sample_row):
        """Tests that add_resource also reduces total_blocked_events."""
        result = simulate_what_if(sample_row, "add_resource")
        
        assert result["total_blocked_events"] < sample_row["total_blocked_events"]
        assert result["total_blocked_events"] == 4  # 5 - 1

    def test_reduce_dependencies(self, sample_row):
        """Tests that reduce_dependencies scenario reduces dependencies."""
        result = simulate_what_if(sample_row, "reduce_dependencies")
        
        assert result["dependencies"] < sample_row["dependencies"]
        assert result["dependencies"] == 2  # 3 - 1

    def test_improve_process_reduces_rework(self, sample_row):
        """Tests that improve_process reduces rework_count."""
        result = simulate_what_if(sample_row, "improve_process")
        
        assert result["rework_count"] < sample_row["rework_count"]
        assert result["rework_count"] == 3  # 4 - 1

    def test_improve_process_reduces_gap(self, sample_row):
        """Tests that improve_process reduces max_progress_gap."""
        result = simulate_what_if(sample_row, "improve_process")
        
        assert result["max_progress_gap"] < sample_row["max_progress_gap"]
        assert result["max_progress_gap"] == 4  # 6 - 2

    def test_values_cannot_go_below_zero(self):
        """Tests that simulated values don't go below zero."""
        row = pd.Series({
            "task_id": "T1",
            "total_blocked_events": 0,
            "dependencies": 0,
            "no_resource_available": 0,
            "rework_count": 0,
            "max_progress_gap": 1,
        })
        
        result = simulate_what_if(row, "add_resource")
        
        assert result["no_resource_available"] == 0
        assert result["total_blocked_events"] == 0

    def test_invalid_scenario_raises_error(self, sample_row):
        """Tests that invalid scenario raises ValueError."""
        with pytest.raises(ValueError) as excinfo:
            simulate_what_if(sample_row, "invalid_scenario")
        
        assert "Unknown scenario" in str(excinfo.value)

    def test_result_is_copy(self, sample_row):
        """Tests that simulated result is a copy, not modifying original."""
        original_value = sample_row["no_resource_available"]
        
        simulate_what_if(sample_row, "add_resource")
        
        assert sample_row["no_resource_available"] == original_value


class TestGetAvailableScenarios:
    """Tests for get_available_scenarios function."""
    
    def test_returns_dict(self):
        """Tests that function returns a dictionary."""
        result = get_available_scenarios()
        assert isinstance(result, dict)

    def test_contains_all_scenarios(self):
        """Tests that all defined scenarios are returned."""
        result = get_available_scenarios()
        
        assert "add_resource" in result
        assert "reduce_dependencies" in result
        assert "improve_process" in result

    def test_contains_description(self):
        """Tests that each scenario has a description."""
        result = get_available_scenarios()
        
        for scenario_id, metadata in result.items():
            assert "description" in metadata
            assert isinstance(metadata["description"], str)

    def test_contains_causal_mechanism(self):
        """Tests that each scenario has causal_mechanism."""
        result = get_available_scenarios()
        
        for scenario_id, metadata in result.items():
            assert "causal_mechanism" in metadata


class TestEstimateScenarioImpact:
    """Tests for estimate_scenario_impact function."""
    
    @pytest.fixture
    def sample_row(self):
        """Creates a sample task feature row."""
        return pd.Series({
            "task_id": "T1",
            "no_resource_available": 5,
            "total_blocked_events": 10,
        })
    
    def test_returns_dict(self, sample_row):
        """Tests that function returns a dictionary."""
        result = estimate_scenario_impact(sample_row, "add_resource")
        assert isinstance(result, dict)

    def test_contains_scenario_info(self, sample_row):
        """Tests that result contains scenario metadata."""
        result = estimate_scenario_impact(sample_row, "add_resource")
        
        assert "scenario" in result
        assert result["scenario"] == "add_resource"
        assert "description" in result

    def test_contains_feature_impacts(self, sample_row):
        """Tests that result contains feature impacts."""
        result = estimate_scenario_impact(sample_row, "add_resource")
        
        assert "feature_impacts" in result
        assert isinstance(result["feature_impacts"], dict)

    def test_feature_impact_structure(self, sample_row):
        """Tests that each feature impact has original, new, and change."""
        result = estimate_scenario_impact(sample_row, "add_resource")
        
        for feature, impact in result["feature_impacts"].items():
            assert "original" in impact
            assert "new" in impact
            assert "change" in impact

    def test_invalid_scenario_returns_error(self, sample_row):
        """Tests that invalid scenario returns error dict."""
        result = estimate_scenario_impact(sample_row, "invalid_scenario")
        
        assert "error" in result


class TestScenarioDefinitions:
    """Tests for SCENARIOS constant."""
    
    def test_scenarios_have_required_fields(self):
        """Tests that all scenarios have required fields."""
        for scenario_id, scenario in SCENARIOS.items():
            assert "description" in scenario, f"{scenario_id} missing description"
            assert "causal_mechanism" in scenario, f"{scenario_id} missing causal_mechanism"
            assert "effects" in scenario, f"{scenario_id} missing effects"
            assert isinstance(scenario["effects"], dict)

    def test_effects_are_numeric(self):
        """Tests that all effect values are numeric."""
        for scenario_id, scenario in SCENARIOS.items():
            for feature, delta in scenario["effects"].items():
                assert isinstance(delta, (int, float)), \
                    f"{scenario_id}.effects.{feature} is not numeric"
