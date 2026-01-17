"""
Analysis Service Module.

Orchestrates the complete risk analysis pipeline:
1. Builds raw data tables from simulation
2. Trains ML model on historical features (with caching)
3. Computes hybrid risk scores for each task
4. Generates explanations and recommendations
5. Runs optional what-if scenarios
6. Persists results to database

This is the main entry point for the FastAPI backend.
"""

from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from data_pipeline.build_raw_tables import build_raw_tables
from models.ml_model import DelayRiskModel, DelayRiskRFModel
from models.hybrid_risk import hybrid_risk_score
from decision_support.explain import explain_risk
from decision_support.actions import recommend_actions
from decision_support.what_if import simulate_what_if
from backend.core.config import load_config
from backend.core.database import save_analysis, list_analyses, get_analysis, get_analysis_stats


# Module-level cache for model and features
_model_cache: Dict[str, Any] = {
    "model": None,
    "features": None,
    "config_hash": None,
}


def _get_config_hash(config: Dict[str, Any]) -> str:
    """Generate a simple hash of config for cache invalidation."""
    model_type = config.get("model", {}).get("type", "logistic")
    return f"{model_type}"


def get_or_train_model(
    config: Dict[str, Any],
    force_retrain: bool = False
) -> tuple:
    """
    Returns cached model and features, or trains new model if needed.
    
    Args:
        config: System configuration
        force_retrain: If True, ignore cache and retrain
    
    Returns:
        Tuple of (model, features DataFrame)
    """
    global _model_cache
    
    config_hash = _get_config_hash(config)
    
    # Check if we can use cached model
    if (
        not force_retrain
        and _model_cache["model"] is not None
        and _model_cache["features"] is not None
        and _model_cache["config_hash"] == config_hash
    ):
        return _model_cache["model"], _model_cache["features"]
    
    # Build data from simulation
    tasks, events, features = build_raw_tables()
    
    # Model selection based on config
    model_type = config.get("model", {}).get("type", "logistic")

    if model_type == "random_forest":
        model: Union[DelayRiskModel, DelayRiskRFModel] = DelayRiskRFModel()
    else:
        model = DelayRiskModel()

    model.train(features)
    
    # Update cache
    _model_cache["model"] = model
    _model_cache["features"] = features
    _model_cache["config_hash"] = config_hash
    
    return model, features


def clear_model_cache() -> None:
    """Clears the model cache, forcing retrain on next request."""
    global _model_cache
    _model_cache = {
        "model": None,
        "features": None,
        "config_hash": None,
    }


def run_analysis(
    what_if: Optional[str] = None,
    force_retrain: bool = False,
    save_to_db: bool = True
) -> List[Dict[str, Any]]:
    """
    Runs the complete project delay risk analysis pipeline.
    
    This function:
    1. Loads system configuration
    2. Gets or trains ML model (with caching)
    3. Computes hybrid risk scores using rules + ML
    4. Generates explanations and action recommendations
    5. Optionally runs what-if scenario analysis
    6. Saves results to database (optional)
    
    Args:
        what_if: Optional scenario to analyze. Supported values:
            - "add_resource": Simulate adding a resource
            - "reduce_dependencies": Simulate reducing dependencies
            - "improve_process": Simulate process improvements
            - None: Skip what-if analysis
        force_retrain: If True, retrain model even if cached
        save_to_db: If True, save results to database
    
    Returns:
        List of task risk assessments, each containing:
            - task_id: Task identifier
            - risk_level: "High", "Medium", or "Low"
            - risk_score: Numeric score 0-100
            - delay_probability: ML-predicted probability
            - reasons: List of risk explanations
            - recommended_actions: List of suggested actions
            - what_if_impact: Optional impact of scenario (if requested)
    """
    config = load_config()
    model_type = config.get("model", {}).get("type", "logistic")

    # Get or train model (with caching)
    model, features = get_or_train_model(config, force_retrain)

    # Analysis loop: score each task
    results: List[Dict[str, Any]] = []

    for _, row in features.iterrows():
        # Get ML probability
        prob = model.predict_proba(features.loc[[_]])[0]
        
        # Compute hybrid risk score (passing config for weights/thresholds)
        risk = hybrid_risk_score(row, prob, config=config)

        # Build response object
        response: Dict[str, Any] = {
            "task_id": row["task_id"],
            "risk_level": risk["risk_level"],
            "risk_score": risk["risk_score"],
            "delay_probability": round(float(prob), 3),
            "reasons": [
                r["text"] if isinstance(r, dict) else r 
                for r in risk["reasons"]
            ],
            "recommended_actions": recommend_actions(row),
        }

        # What-if analysis (optional)
        if what_if:
            simulated = simulate_what_if(row, what_if)
            # Create modified features for prediction
            modified_features = features.loc[[row.name]].assign(**simulated.to_dict())
            new_prob = model.predict_proba(modified_features)[0]

            response["what_if_impact"] = {
                "scenario": what_if,
                "new_delay_probability": round(float(new_prob), 3),
                "probability_reduction": round(float(prob - new_prob), 3)
            }

        results.append(response)

    # Save to database
    if save_to_db:
        try:
            save_analysis(
                results=results,
                what_if_scenario=what_if,
                model_type=model_type
            )
        except Exception:
            # Log but don't fail if database save fails
            pass

    return results


def get_analysis_history(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Gets the history of recent analyses.
    
    Args:
        limit: Maximum number of analyses to return
        
    Returns:
        List of analysis summary dictionaries
    """
    return list_analyses(limit=limit)


def get_analysis_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
    """
    Gets a specific analysis by ID.
    
    Args:
        analysis_id: Analysis ID
        
    Returns:
        Full analysis with results, or None if not found
    """
    return get_analysis(analysis_id)


def get_stats() -> Dict[str, Any]:
    """
    Gets aggregate statistics from all analyses.
    
    Returns:
        Dictionary with stats like total analyses, risk counts, etc.
    """
    return get_analysis_stats()

