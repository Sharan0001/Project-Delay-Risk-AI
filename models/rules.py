"""
Rule-Based Risk Assessment Module.

Implements domain expert knowledge as explicit, interpretable rules.
These rules are *not* learned from data - they encode known causal
relationships between project signals and delay risk.

Design Philosophy:
- Rules are first-class citizens; they provide audit trails
- ML supplements rules, not the other way around
- Each rule has a defined severity and score contribution

Thresholds are based on project management heuristics:
- 3+ blocked events: Indicates systemic issues
- 2+ dependencies: High coupling increases coordination overhead
- 1+ resource unavailability: Bottleneck indicator
- 2+ rework events: Quality issues causing iteration
- 4+ day progress gap: Stagnation or hidden problems
"""

from typing import Dict, Any, List, Tuple


# Rule definitions with thresholds and scores
# Format: (field, threshold, score_contribution, severity, reason)
RULES = [
    {
        "field": "total_blocked_events",
        "threshold": 3,
        "score": 25,
        "severity": "critical",
        "reason": "Frequent task blocking (3+ events)",
        "rationale": "Recurring blocks indicate systemic issues beyond random disruptions"
    },
    {
        "field": "dependencies",
        "threshold": 2,
        "score": 15,
        "severity": "warning",
        "reason": "Heavy dependency constraints (2+ deps)",
        "rationale": "High coupling increases coordination overhead and failure propagation"
    },
    {
        "field": "no_resource_available",
        "threshold": 1,
        "score": 20,
        "severity": "critical",
        "reason": "Insufficient resource availability",
        "rationale": "Resource bottlenecks are a primary cause of project delays"
    },
    {
        "field": "rework_count",
        "threshold": 2,
        "score": 15,
        "severity": "warning",
        "reason": "Repeated rework events (2+ occurrences)",
        "rationale": "Rework indicates quality issues or requirement instability"
    },
    {
        "field": "max_progress_gap",
        "threshold": 4,
        "score": 15,
        "severity": "warning",
        "reason": "Long progress stagnation (4+ days)",
        "rationale": "Large gaps often hide problems or indicate blocked work"
    },
]


def rule_based_risk(row: Dict[str, Any]) -> Tuple[int, List[Dict[str, str]]]:
    """
    Computes an interpretable risk score (0–100) based on domain rules.
    
    This function evaluates a set of predefined rules against task features.
    Each triggered rule contributes to the total score and provides an
    explanation with severity level.
    
    Args:
        row: Feature dictionary/Series for a single task, must contain:
            - total_blocked_events: Count of blocking events
            - dependencies: Count of dependency-related blocks
            - no_resource_available: Count of resource unavailability events
            - rework_count: Number of rework cycles
            - max_progress_gap: Longest gap between progress updates (days)
    
    Returns:
        Tuple of:
            - score: Integer risk score capped at 100
            - reasons: List of dicts with 'text' and 'severity' keys
    
    Example:
        >>> score, reasons = rule_based_risk(task_features)
        >>> for r in reasons:
        ...     print(f"[{r['severity']}] {r['text']}")
        [critical] Frequent task blocking (3+ events)
    """
    score = 0
    reasons: List[Dict[str, str]] = []

    for rule in RULES:
        field_value = row.get(rule["field"], 0)
        
        if field_value >= rule["threshold"]:
            score += rule["score"]
            reasons.append({
                "text": rule["reason"],
                "severity": rule["severity"]
            })

    # Cap score at 100
    return min(score, 100), reasons


def get_rule_definitions() -> List[Dict[str, Any]]:
    """
    Returns the complete rule definitions for documentation/audit purposes.
    
    This allows external systems to inspect and display the rules
    that drive risk assessment.
    
    Returns:
        List of rule definition dictionaries
    """
    return RULES.copy()
