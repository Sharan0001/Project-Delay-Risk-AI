"""
Risk Explanation Module.

Generates human-readable explanations for risk assessments.
Combines rule-based reasoning with ML feature importance to provide
a comprehensive view of why a task is considered risky.

Explanation Strategy:
1. Rule triggers: Explicit threshold-based conditions
2. ML feature contribution: Model-derived importance with direction
3. Combined narrative: Actionable insights for decision makers
"""

from typing import Dict, List, Any, Union


def explain_risk(
    row: Dict[str, Any], 
    ml_model: Any
) -> List[str]:
    """
    Generates comprehensive risk explanations combining rules and ML signals.
    
    This function provides explainability at two levels:
    1. Domain Rules: Deterministic, threshold-based triggers
    2. ML Features: Statistical patterns learned from data
    
    The explanations are designed to be:
    - Human-readable for project managers
    - Actionable for risk mitigation
    - Auditable for decision traceability
    
    Args:
        row: Feature dictionary/Series for a single task
        ml_model: Trained model with get_feature_importance() method
    
    Returns:
        List of explanation strings, ordered by importance
        
    Example:
        >>> explanations = explain_risk(task_features, trained_model)
        >>> for e in explanations:
        ...     print(f"• {e}")
        • Frequent task blocking observed (5 events)
        • Top risk factor: total_blocked_events (increases risk)
    """
    explanations: List[str] = []

    # -----------------------------
    # Rule-based explanations
    # Import from centralized rules to avoid duplication
    # -----------------------------
    from models.rules import RULES
    
    for rule in RULES:
        field_value = row.get(rule["field"], 0)
        if field_value >= rule["threshold"]:
            # Add explanation with actual value
            explanations.append(
                f"{rule['reason']} ({int(field_value)} occurrences)"
            )

    # -----------------------------
    # ML-based explanation
    # Feature importance with direction
    # -----------------------------
    try:
        importance = ml_model.get_feature_importance()
        
        # Sort by absolute importance
        sorted_features = sorted(
            importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:3]  # Top 3 features
        
        # Format with direction information
        feature_explanations = []
        for feature_name, importance_value in sorted_features:
            # Check actual feature value for this task
            feature_val = row.get(feature_name, 0)
            
            # Determine direction (for logistic regression, sign matters)
            # For RF, all values are positive so we just report importance
            if importance_value > 0:
                direction = "increases risk"
            elif importance_value < 0:
                direction = "decreases risk"
            else:
                direction = "neutral"
            
            # Only include if feature has non-zero value for this task
            if feature_val > 0:
                feature_explanations.append(
                    f"{feature_name.replace('_', ' ')} = {feature_val:.0f} ({direction})"
                )
        
        if feature_explanations:
            explanations.append(
                "ML risk drivers: " + ", ".join(feature_explanations)
            )
        else:
            # Fallback: just list top features by name
            top_names = [name for name, _ in sorted_features]
            explanations.append(
                "Top ML risk factors: " + ", ".join(top_names)
            )
            
    except Exception:
        # Graceful degradation if model doesn't support feature importance
        explanations.append("ML model analysis unavailable")

    return explanations


def get_explanation_summary(
    row: Dict[str, Any],
    risk_result: Dict[str, Any]
) -> str:
    """
    Generates a one-line summary of the risk assessment.
    
    Useful for dashboards and quick overviews.
    
    Args:
        row: Task feature dictionary
        risk_result: Result from hybrid_risk_score()
    
    Returns:
        Single-line summary string
    """
    level = risk_result.get("risk_level", "Unknown")
    score = risk_result.get("risk_score", 0)
    reasons = risk_result.get("reasons", [])
    
    reason_count = len(reasons)
    primary = reasons[0]["text"] if reasons and isinstance(reasons[0], dict) else ""
    
    if reason_count == 0:
        return f"{level} risk (score: {score}) - No specific concerns"
    elif reason_count == 1:
        return f"{level} risk (score: {score}) - {primary}"
    else:
        return f"{level} risk (score: {score}) - {primary} (+{reason_count-1} more)"
