"""
Action Recommendation Module.

Converts risk signals into actionable recommendations for project managers.
Each recommendation is based on triggered risk conditions and includes
priority information for triage.

Priority Levels:
- HIGH: Immediate action required, significant delay risk
- MEDIUM: Should address soon, moderate impact
- LOW: Monitor and address proactively

Design: Action thresholds are derived from the centralized RULES module
to ensure consistency and avoid duplication.
"""

from typing import Dict, Any, List
from models.rules import RULES


def _build_actions_from_rules() -> List[Dict[str, Any]]:
    """
    Builds action definitions by deriving thresholds from RULES.
    
    This ensures that action triggers are always consistent with
    the rule-based risk assessment.
    """
    # Map fields to actions and priorities
    action_mapping = {
        "no_resource_available": {
            "priority": "HIGH",
            "action": "Allocate additional resources to this task",
            "rationale": "Resource bottlenecks directly cause delays"
        },
        "total_blocked_events": {
            "priority": "HIGH",
            "action": "Conduct root cause analysis for recurring blocks",
            "rationale": "Systemic blocking indicates process or dependency issues"
        },
        "dependencies": {
            "priority": "MEDIUM",
            "action": "Review and reduce task dependencies if possible",
            "rationale": "High coupling propagates delays across tasks"
        },
        "rework_count": {
            "priority": "MEDIUM",
            "action": "Investigate quality issues causing rework",
            "rationale": "Rework indicates unclear requirements or technical debt"
        },
        "max_progress_gap": {
            "priority": "MEDIUM",
            "action": "Increase monitoring frequency or enforce daily updates",
            "rationale": "Large gaps hide problems and delay detection"
        },
    }
    
    actions = []
    for rule in RULES:
        field = rule["field"]
        if field in action_mapping:
            actions.append({
                "field": field,
                "threshold": rule["threshold"],  # Derived from RULES
                **action_mapping[field]
            })
    
    return actions


# Build actions from rules at module load time
ACTIONS = _build_actions_from_rules()


def recommend_actions(row: Dict[str, Any]) -> List[str]:
    """
    Generates prioritized action recommendations based on risk signals.
    
    This function maps risk indicators to specific, actionable steps
    that project managers can take to mitigate delay risk.
    
    The recommendations are:
    - Prioritized (HIGH actions first)
    - Specific (not generic advice)
    - Actionable (clearly executable)
    
    Args:
        row: Feature dictionary/Series for a single task
    
    Returns:
        List of action strings, sorted by priority (HIGH first)
        
    Example:
        >>> actions = recommend_actions(task_features)
        >>> for a in actions:
        ...     print(f"• {a}")
        • [HIGH] Allocate additional resources to this task
    """
    triggered_actions: List[Dict[str, Any]] = []

    for action_def in ACTIONS:
        field_value = row.get(action_def["field"], 0)
        
        if field_value >= action_def["threshold"]:
            triggered_actions.append({
                "priority": action_def["priority"],
                "action": action_def["action"],
                "rationale": action_def["rationale"]
            })

    # Sort by priority (HIGH first)
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    triggered_actions.sort(key=lambda x: priority_order.get(x["priority"], 99))
    
    # Format actions with priority prefix
    actions = [
        f"[{a['priority']}] {a['action']}"
        for a in triggered_actions
    ]
    
    if not actions:
        actions.append("Continue monitoring – no immediate action required")

    return actions


def get_action_details(row: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Returns detailed action recommendations with full metadata.
    
    Unlike recommend_actions() which returns formatted strings,
    this function returns structured data for programmatic use.
    
    Args:
        row: Feature dictionary/Series for a single task
    
    Returns:
        List of action dictionaries with priority, action, and rationale
    """
    triggered: List[Dict[str, Any]] = []

    for action_def in ACTIONS:
        field_value = row.get(action_def["field"], 0)
        
        if field_value >= action_def["threshold"]:
            triggered.append({
                "priority": action_def["priority"],
                "action": action_def["action"],
                "rationale": action_def["rationale"],
                "triggered_by": action_def["field"],
                "current_value": field_value,
                "threshold": action_def["threshold"]
            })

    # Sort by priority
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    triggered.sort(key=lambda x: priority_order.get(x["priority"], 99))
    
    return triggered
