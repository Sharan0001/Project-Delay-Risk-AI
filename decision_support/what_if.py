"""
What-If Analysis Module.

Provides counterfactual simulation for risk scenarios.
Allows decision makers to explore "What would happen if...?" questions.

Current Approach (Feature Perturbation):
- Simple heuristic-based feature modification
- Fast but approximate
- Good for quick exploratory analysis

Future Direction (Simulation-Backed):
- Could be extended to re-run actual project simulation
- Would provide more realistic causal estimates
- Requires more computational resources
"""

from typing import Dict, Any
import pandas as pd


# Scenario definitions with their effects
SCENARIOS = {
    "add_resource": {
        "description": "Add one resource to the project",
        "causal_mechanism": "Reduces resource bottlenecks and blocking",
        "effects": {
            "no_resource_available": -1,
            "total_blocked_events": -1,
        }
    },
    "reduce_dependencies": {
        "description": "Reduce task coupling through refactoring",
        "causal_mechanism": "Decreases coordination overhead and failure propagation",
        "effects": {
            "dependencies": -2,  # Reduce dependency-related blocks
            "total_blocked_events": -1,  # Overall blocking reduction
        }
    },
    "improve_process": {
        "description": "Implement quality improvements and better monitoring",
        "causal_mechanism": "Reduces rework cycles and progress stagnation",
        "effects": {
            "rework_count": -1,
            "max_progress_gap": -2,
        }
    },
}


def simulate_what_if(
    row: pd.Series,
    scenario: str
) -> pd.Series:
    """
    Simulates how risk-related features would change under a management action.
    
    This function performs counterfactual analysis by modifying task features
    according to predefined scenario effects. It answers questions like:
    "If we add a resource, how would the risk profile change?"
    
    Causal Assumptions:
    - add_resource: Reduces resource unavailability by 1, total blocks by 1
    - reduce_dependencies: Reduces dependency count by 1
    - improve_process: Reduces rework by 1 and progress gaps by 2 days
    
    These are simplified heuristics. In production, consider:
    - Using actual simulation with modified parameters
    - Calibrating effects from historical data
    - Modeling uncertainty in effect sizes
    
    Args:
        row: Pandas Series with task feature values
        scenario: Scenario identifier (one of SCENARIOS.keys())
    
    Returns:
        Modified Series with adjusted feature values
    
    Raises:
        ValueError: If scenario is not recognized
        
    Example:
        >>> modified = simulate_what_if(task_row, "add_resource")
        >>> new_prob = model.predict_proba(modified)
    """
    if scenario not in SCENARIOS:
        valid = list(SCENARIOS.keys())
        raise ValueError(f"Unknown scenario '{scenario}'. Valid: {valid}")
    
    simulated = row.copy()
    effects = SCENARIOS[scenario]["effects"]
    
    for feature, delta in effects.items():
        if feature in simulated.index:
            # Apply effect, ensuring we don't go below 0
            current = simulated[feature]
            simulated[feature] = max(0, current + delta)

    return simulated


def get_available_scenarios() -> Dict[str, Dict[str, str]]:
    """
    Returns available what-if scenarios with descriptions.
    
    Useful for populating UI dropdowns and documentation.
    
    Returns:
        Dictionary mapping scenario IDs to their metadata
    """
    return {
        key: {
            "description": val["description"],
            "causal_mechanism": val["causal_mechanism"]
        }
        for key, val in SCENARIOS.items()
    }


def estimate_scenario_impact(
    row: pd.Series,
    scenario: str
) -> Dict[str, Any]:
    """
    Estimates the direct impact of a scenario without running the model.
    
    Useful for showing immediate feature changes before computing
    new predictions.
    
    Args:
        row: Original task features
        scenario: Scenario to analyze
        
    Returns:
        Dictionary with feature changes
    """
    if scenario not in SCENARIOS:
        return {"error": f"Unknown scenario: {scenario}"}
    
    effects = SCENARIOS[scenario]["effects"]
    impacts = {}
    
    for feature, delta in effects.items():
        original = row.get(feature, 0)
        new_val = max(0, original + delta)
        impacts[feature] = {
            "original": original,
            "new": new_val,
            "change": new_val - original
        }
    
    return {
        "scenario": scenario,
        "description": SCENARIOS[scenario]["description"],
        "feature_impacts": impacts
    }
