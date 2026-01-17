"""
Unit tests for the feature engineering module.

Tests:
- Block feature computation
- Progress feature computation
- Stagnation feature computation
- Master feature builder
"""

import pytest
import pandas as pd
from data_pipeline.features import (
    compute_block_features,
    compute_progress_features,
    compute_stagnation_features,
    build_task_features,
)


class TestComputeBlockFeatures:
    """Tests for compute_block_features function."""
    
    def test_empty_events(self):
        """Empty events should produce empty result."""
        events = pd.DataFrame({
            "task_id": [],
            "event_type": [],
            "reason": [],
        })
        
        result = compute_block_features(events)
        
        assert len(result) == 0
    
    def test_no_blocked_events(self):
        """Events without blocked type should produce empty result."""
        events = pd.DataFrame({
            "task_id": ["T1", "T1", "T2"],
            "event_type": ["progress", "complete", "start"],
            "reason": [None, None, None],
        })
        
        result = compute_block_features(events)
        
        assert len(result) == 0
    
    def test_single_blocked_event(self):
        """Single blocked event should be counted."""
        events = pd.DataFrame({
            "task_id": ["T1"],
            "event_type": ["blocked"],
            "reason": ["dependencies"],
        })
        
        result = compute_block_features(events)
        
        assert len(result) == 1
        assert result.iloc[0]["task_id"] == "T1"
        assert result.iloc[0]["dependencies"] == 1
        assert result.iloc[0]["total_blocked_events"] == 1
    
    def test_multiple_block_reasons(self):
        """Multiple block reasons should be counted separately."""
        events = pd.DataFrame({
            "task_id": ["T1", "T1", "T1", "T1"],
            "event_type": ["blocked", "blocked", "blocked", "blocked"],
            "reason": ["dependencies", "dependencies", "no_resource_available", "external_block"],
        })
        
        result = compute_block_features(events)
        
        assert len(result) == 1
        assert result.iloc[0]["dependencies"] == 2
        assert result.iloc[0]["no_resource_available"] == 1
        assert result.iloc[0]["external_block"] == 1
        assert result.iloc[0]["total_blocked_events"] == 4
    
    def test_all_expected_columns_present(self):
        """Result should have all expected block columns."""
        events = pd.DataFrame({
            "task_id": ["T1"],
            "event_type": ["blocked"],
            "reason": ["dependencies"],
        })
        
        result = compute_block_features(events)
        
        expected_cols = [
            "task_id",
            "dependencies",
            "no_resource_available",
            "skill_mismatch",
            "external_block",
            "random_disruption",
            "total_blocked_events",
        ]
        for col in expected_cols:
            assert col in result.columns


class TestComputeProgressFeatures:
    """Tests for compute_progress_features function."""
    
    def test_empty_events(self):
        """Empty events should produce empty result."""
        events = pd.DataFrame({
            "task_id": [],
            "event_type": [],
            "day": [],
        })
        
        result = compute_progress_features(events)
        
        assert len(result) == 0
    
    def test_progress_events_counted(self):
        """Progress events should be counted."""
        events = pd.DataFrame({
            "task_id": ["T1", "T1", "T1"],
            "event_type": ["progress", "progress", "progress"],
            "day": [1, 2, 3],
        })
        
        result = compute_progress_features(events)
        
        assert len(result) == 1
        assert result.iloc[0]["progress_events"] == 3
        assert result.iloc[0]["first_progress_day"] == 1
        assert result.iloc[0]["last_progress_day"] == 3
    
    def test_rework_events_counted(self):
        """Rework events should be counted separately."""
        events = pd.DataFrame({
            "task_id": ["T1", "T1", "T1"],
            "event_type": ["progress", "rework", "rework"],
            "day": [1, 2, 3],
        })
        
        result = compute_progress_features(events)
        
        assert len(result) == 1
        assert result.iloc[0]["rework_count"] == 2
    
    def test_no_rework_defaults_to_zero(self):
        """No rework events should result in rework_count = 0."""
        events = pd.DataFrame({
            "task_id": ["T1"],
            "event_type": ["progress"],
            "day": [1],
        })
        
        result = compute_progress_features(events)
        
        assert result.iloc[0]["rework_count"] == 0


class TestComputeStagnationFeatures:
    """Tests for compute_stagnation_features function."""
    
    def test_single_progress_event(self):
        """Single progress event should have 0 gap."""
        events = pd.DataFrame({
            "task_id": ["T1"],
            "event_type": ["progress"],
            "day": [5],
        })
        
        result = compute_stagnation_features(events)
        
        assert len(result) == 1
        assert result.iloc[0]["max_progress_gap"] == 0
    
    def test_consecutive_days_minimal_gap(self):
        """Consecutive days should have gap of 1."""
        events = pd.DataFrame({
            "task_id": ["T1", "T1", "T1"],
            "event_type": ["progress", "progress", "progress"],
            "day": [1, 2, 3],
        })
        
        result = compute_stagnation_features(events)
        
        assert result.iloc[0]["max_progress_gap"] == 1
    
    def test_large_gap_detected(self):
        """Large gaps between progress should be detected."""
        events = pd.DataFrame({
            "task_id": ["T1", "T1"],
            "event_type": ["progress", "progress"],
            "day": [1, 10],
        })
        
        result = compute_stagnation_features(events)
        
        assert result.iloc[0]["max_progress_gap"] == 9
    
    def test_max_gap_found_among_multiple(self):
        """Should find the maximum gap among multiple."""
        events = pd.DataFrame({
            "task_id": ["T1", "T1", "T1", "T1"],
            "event_type": ["progress", "progress", "progress", "progress"],
            "day": [1, 3, 5, 15],  # gaps: 2, 2, 10
        })
        
        result = compute_stagnation_features(events)
        
        assert result.iloc[0]["max_progress_gap"] == 10


class TestBuildTaskFeatures:
    """Tests for build_task_features function."""
    
    def test_combines_all_features(self):
        """Should combine block, progress, and stagnation features."""
        tasks = pd.DataFrame({
            "task_id": ["T1"],
            "planned_duration": [5],
        })
        
        events = pd.DataFrame({
            "task_id": ["T1", "T1", "T1"],
            "event_type": ["blocked", "progress", "progress"],
            "reason": ["dependencies", None, None],
            "day": [1, 2, 5],
        })
        
        result = build_task_features(tasks, events)
        
        assert len(result) == 1
        assert "dependencies" in result.columns
        assert "progress_events" in result.columns
        assert "max_progress_gap" in result.columns
    
    def test_missing_values_filled_with_zero(self):
        """Missing numeric values should be filled with 0."""
        tasks = pd.DataFrame({
            "task_id": ["T1", "T2"],
            "planned_duration": [5, 5],
        })
        
        # T1 has block and progress events, T2 has only progress (no blocks)
        events = pd.DataFrame({
            "task_id": ["T1", "T1", "T2"],
            "event_type": ["blocked", "progress", "progress"],
            "reason": ["dependencies", None, None],
            "day": [1, 2, 3],
        })
        
        result = build_task_features(tasks, events)
        
        assert len(result) == 2
        # T2 should have 0 for dependencies (no block events)
        t2_row = result[result["task_id"] == "T2"].iloc[0]
        assert t2_row["dependencies"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
