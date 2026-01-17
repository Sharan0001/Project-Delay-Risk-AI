"""
Hybrid Risk Scoring Module.

Combines rule-based domain reasoning with ML probability estimates
to produce a final risk decision. This approach ensures:

1. Interpretability: Rules provide clear, auditable reasoning
2. Adaptability: ML captures patterns not explicitly coded
3. Robustness: Neither system dominates; weighted combination

The hybrid score follows the formula:
    final_score = rule_weight * rule_score + ml_weight * (ml_probability * 100)

Risk Levels (configurable thresholds):
    - High: score >= high_threshold (default 70)
    - Medium: score >= medium_threshold (default 40)
    - Low: score < medium_threshold
"""

from typing import Dict, Any, Optional, Tuple, List
from models.rules import rule_based_risk


# Default weights for rule vs ML contribution
DEFAULT_RULE_WEIGHT = 0.6
DEFAULT_ML_WEIGHT = 0.4

# Default risk level thresholds
DEFAULT_HIGH_THRESHOLD = 70
DEFAULT_MEDIUM_THRESHOLD = 40


def hybrid_risk_score(
    row: Dict[str, Any],
    ml_probability: float,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Combines rule-based reasoning with ML probability to produce a final risk decision.
    
    This is the core decision function of the system. It:
    1. Evaluates domain rules to get an interpretable score
    2. Scales ML probability to a 0-100 range
    3. Combines both signals using configurable weights
    4. Classifies into risk levels
    
    Args:
        row: Feature dictionary/Series for a single task
        ml_probability: Model-predicted probability of delay (0.0 to 1.0)
        config: Optional configuration dict with keys:
            - risk_weights.rule_weight: Weight for rule score (default 0.6)
            - risk_weights.ml_weight: Weight for ML score (default 0.4)
            - risk_thresholds.high: Score threshold for High risk (default 70)
            - risk_thresholds.medium: Score threshold for Medium risk (default 40)
    
    Returns:
        Dictionary containing:
            - risk_score: Final combined score (0-100)
            - risk_level: Classification ("High", "Medium", "Low")
            - reasons: List of rule-triggered explanations
            - ml_probability: Original ML probability
            - rule_score: Score from rules alone
            - weights_used: The weights used for combination
    
    Example:
        >>> risk = hybrid_risk_score(task_features, 0.75)
        >>> print(f"Risk: {risk['risk_level']} ({risk['risk_score']})")
        Risk: High (78)
    """
    # Extract weights from config or use defaults
    rule_weight = DEFAULT_RULE_WEIGHT
    ml_weight = DEFAULT_ML_WEIGHT
    high_threshold = DEFAULT_HIGH_THRESHOLD
    medium_threshold = DEFAULT_MEDIUM_THRESHOLD
    
    if config:
        weights = config.get("risk_weights", {})
        rule_weight = weights.get("rule_weight", DEFAULT_RULE_WEIGHT)
        ml_weight = weights.get("ml_weight", DEFAULT_ML_WEIGHT)
        
        thresholds = config.get("risk_thresholds", {})
        high_threshold = thresholds.get("high", DEFAULT_HIGH_THRESHOLD)
        medium_threshold = thresholds.get("medium", DEFAULT_MEDIUM_THRESHOLD)

    # Get rule-based assessment
    rule_score, reasons = rule_based_risk(row)

    # Combine scores using weighted average
    # Rule score is already 0-100, ML probability is 0-1 so we scale to 0-100
    final_score = int(
        rule_weight * rule_score +
        ml_weight * (ml_probability * 100)
    )
    
    # Ensure score stays in valid range
    final_score = max(0, min(100, final_score))

    # Determine risk level based on thresholds
    if final_score >= high_threshold:
        level = "High"
    elif final_score >= medium_threshold:
        level = "Medium"
    else:
        level = "Low"

    return {
        "risk_score": final_score,
        "risk_level": level,
        "reasons": reasons,
        "ml_probability": round(float(ml_probability), 3),
        "rule_score": rule_score,
        "weights_used": {
            "rule_weight": rule_weight,
            "ml_weight": ml_weight
        }
    }
