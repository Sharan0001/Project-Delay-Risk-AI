"""
Integration Tests for the Project Delay Risk AI System.

Tests the complete analysis pipeline from simulation to risk scoring.
"""

import pytest
from typing import Dict, Any

from data_pipeline.build_raw_tables import build_raw_tables
from models.ml_model import DelayRiskModel, DelayRiskRFModel
from models.hybrid_risk import hybrid_risk_score
from decision_support.explain import explain_risk
from decision_support.actions import recommend_actions
from decision_support.what_if import simulate_what_if


class TestFullPipeline:
    """Tests the complete analysis pipeline."""

    def test_pipeline_produces_valid_output(self):
        """Tests that the pipeline produces valid risk assessments."""
        # Build data with small simulation for speed
        tasks, events, features = build_raw_tables(num_tasks=10, seed=42)
        
        # Train model
        model = DelayRiskModel()
        model.train(features)
        
        # Score each task
        for _, row in features.iterrows():
            prob = model.predict_proba(features.loc[[_]])[0]
            risk = hybrid_risk_score(row, prob)
            
            # Validate output
            assert risk["risk_level"] in ["High", "Medium", "Low"]
            assert 0 <= risk["risk_score"] <= 100
            assert 0 <= risk["ml_probability"] <= 1
            assert isinstance(risk["reasons"], list)

    def test_pipeline_with_random_forest(self):
        """Tests the pipeline with Random Forest model."""
        tasks, events, features = build_raw_tables(num_tasks=10, seed=42)
        
        model = DelayRiskRFModel()
        model.train(features)
        
        for _, row in features.iterrows():
            prob = model.predict_proba(features.loc[[_]])[0]
            risk = hybrid_risk_score(row, prob)
            
            assert risk["risk_level"] in ["High", "Medium", "Low"]
            assert 0 <= risk["risk_score"] <= 100

    def test_explanations_generated(self):
        """Tests that explanations are generated for tasks."""
        tasks, events, features = build_raw_tables(num_tasks=10, seed=42)
        
        model = DelayRiskModel()
        model.train(features)
        
        for _, row in features.iterrows():
            explanations = explain_risk(row, model)
            
            # Explanations should be a list of strings
            assert isinstance(explanations, list)
            # At least some tasks should have explanations
            # (not all will, depending on thresholds)

    def test_actions_generated(self):
        """Tests that recommendations are generated."""
        tasks, events, features = build_raw_tables(num_tasks=10, seed=42)
        
        for _, row in features.iterrows():
            actions = recommend_actions(row)
            
            assert isinstance(actions, list)


class TestWhatIfAnalysis:
    """Tests the what-if scenario analysis."""

    def test_add_resource_reduces_probability(self):
        """Tests that adding a resource can reduce delay probability."""
        tasks, events, features = build_raw_tables(num_tasks=20, seed=42)
        
        model = DelayRiskModel()
        model.train(features)
        
        # Find a task with resource issues
        for _, row in features.iterrows():
            if row.get("no_resource_available", 0) > 0:
                original_prob = model.predict_proba(features.loc[[_]])[0]
                
                simulated = simulate_what_if(row, "add_resource")
                modified = features.loc[[row.name]].assign(**simulated.to_dict())
                new_prob = model.predict_proba(modified)[0]
                
                # New probability should be equal or lower
                assert new_prob <= original_prob + 0.01  # Allow small tolerance
                break

    def test_all_scenarios_return_valid_data(self):
        """Tests that all scenarios return valid modified features."""
        tasks, events, features = build_raw_tables(num_tasks=5, seed=42)
        
        scenarios = ["add_resource", "reduce_dependencies", "improve_process"]
        
        for _, row in features.iterrows():
            for scenario in scenarios:
                simulated = simulate_what_if(row, scenario)
                
                # Simulated should be a series with the same index
                assert simulated is not None


class TestModelPersistence:
    """Tests model save/load functionality."""

    def test_save_and_load_logistic(self, tmp_path):
        """Tests saving and loading Logistic Regression model."""
        tasks, events, features = build_raw_tables(num_tasks=10, seed=42)
        
        # Train and save
        model = DelayRiskModel()
        model.train(features)
        original_pred = model.predict_proba(features)[0]
        
        model_path = tmp_path / "test_model.pkl"
        model.save(model_path)
        
        # Load and compare
        loaded_model = DelayRiskModel.from_file(model_path)
        loaded_pred = loaded_model.predict_proba(features)[0]
        
        assert abs(original_pred - loaded_pred) < 0.001

    def test_save_and_load_random_forest(self, tmp_path):
        """Tests saving and loading Random Forest model."""
        tasks, events, features = build_raw_tables(num_tasks=10, seed=42)
        
        model = DelayRiskRFModel()
        model.train(features)
        original_pred = model.predict_proba(features)[0]
        
        model_path = tmp_path / "test_rf_model.pkl"
        model.save(model_path)
        
        loaded_model = DelayRiskRFModel.from_file(model_path)
        loaded_pred = loaded_model.predict_proba(features)[0]
        
        assert abs(original_pred - loaded_pred) < 0.001


class TestValidation:
    """Tests data validation."""

    def test_pipeline_validates_data(self):
        """Tests that the pipeline validates data correctly."""
        # This should run without raising validation errors
        tasks, events, features = build_raw_tables(num_tasks=10, seed=42)
        
        assert len(tasks) >= 10
        assert len(events) > 0
        assert len(features) >= 10
