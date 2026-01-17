"""
Pytest configuration and shared fixtures.

This file is automatically loaded by pytest and provides
fixtures available to all test modules.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_task_features():
    """Sample task features for testing."""
    return {
        "task_id": "T1",
        "total_blocked_events": 2,
        "dependencies": 1,
        "no_resource_available": 0,
        "external_block": 0,
        "random_disruption": 0,
        "rework_count": 1,
        "max_progress_gap": 2,
        "progress_events": 5,
        "planned_duration": 5,
    }


@pytest.fixture
def high_risk_features():
    """Task features that trigger all risk rules."""
    return {
        "task_id": "T_HIGH",
        "total_blocked_events": 10,
        "dependencies": 5,
        "no_resource_available": 3,
        "external_block": 2,
        "random_disruption": 2,
        "rework_count": 4,
        "max_progress_gap": 8,
        "progress_events": 15,
        "planned_duration": 5,
    }


@pytest.fixture
def low_risk_features():
    """Task features with no risk triggers."""
    return {
        "task_id": "T_LOW",
        "total_blocked_events": 0,
        "dependencies": 0,
        "no_resource_available": 0,
        "external_block": 0,
        "random_disruption": 0,
        "rework_count": 0,
        "max_progress_gap": 0,
        "progress_events": 10,
        "planned_duration": 5,
    }


@pytest.fixture
def sample_config():
    """Sample system configuration."""
    return {
        "simulation": {
            "seed": 42,
            "max_days": 120
        },
        "risk_weights": {
            "rule_weight": 0.6,
            "ml_weight": 0.4
        },
        "risk_thresholds": {
            "high": 70,
            "medium": 40
        },
        "model": {
            "type": "logistic"
        }
    }
