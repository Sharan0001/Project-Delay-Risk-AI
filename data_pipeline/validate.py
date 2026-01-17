"""
Data Validation Module.

Provides comprehensive data quality checks for task and event data.
All validation functions return a list of error messages (empty = valid).

Validation Categories:
- Schema validation (required columns, data types)
- Value validation (ranges, enums)
- Logical validation (constraints, relationships)
"""

import pandas as pd
from typing import List


# Expected columns for each data type
REQUIRED_TASK_COLUMNS = [
    "task_id", "planned_duration", "complexity", "priority",
    "required_skill", "status"
]

REQUIRED_EVENT_COLUMNS = [
    "day", "task_id", "event_type"
]

# Valid values for categorical fields
VALID_STATUSES = {"not_started", "in_progress", "blocked", "completed"}
VALID_PRIORITIES = {"high", "medium", "low"}
VALID_EVENT_TYPES = {"start", "progress", "blocked", "rework", "complete"}


def validate_tasks(tasks: pd.DataFrame) -> List[str]:
    """
    Validates task data quality.
    
    Checks:
    - Required columns exist
    - No NaN in critical fields
    - planned_duration > 0
    - complexity in [1, 5]
    - priority is valid
    - status is valid
    - actual_end >= actual_start (for completed tasks)
    
    Args:
        tasks: Task DataFrame to validate
    
    Returns:
        List of error messages (empty if valid)
    """
    errors: List[str] = []
    
    # Check required columns
    missing_cols = [col for col in REQUIRED_TASK_COLUMNS if col not in tasks.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
        return errors  # Can't continue without required columns
    
    # Check for NaN in critical fields
    for col in ["task_id", "planned_duration", "complexity"]:
        if col in tasks.columns and tasks[col].isna().any():
            nan_count = tasks[col].isna().sum()
            errors.append(f"Found {nan_count} NaN values in '{col}'")
    
    # Validate planned_duration
    if (tasks["planned_duration"] <= 0).any():
        bad_count = (tasks["planned_duration"] <= 0).sum()
        errors.append(f"planned_duration must be positive ({bad_count} violations)")
    
    # Validate complexity range
    if (tasks["complexity"] < 1).any() or (tasks["complexity"] > 5).any():
        bad_count = ((tasks["complexity"] < 1) | (tasks["complexity"] > 5)).sum()
        errors.append(f"complexity must be in [1, 5] ({bad_count} violations)")
    
    # Validate priority values
    if "priority" in tasks.columns:
        invalid_priorities = ~tasks["priority"].isin(VALID_PRIORITIES)
        if invalid_priorities.any():
            bad_values = tasks.loc[invalid_priorities, "priority"].unique().tolist()
            errors.append(f"Invalid priority values: {bad_values}")
    
    # Validate status values
    if "status" in tasks.columns:
        invalid_statuses = ~tasks["status"].isin(VALID_STATUSES)
        if invalid_statuses.any():
            bad_values = tasks.loc[invalid_statuses, "status"].unique().tolist()
            errors.append(f"Invalid status values: {bad_values}")
    
    # Validate actual_end >= actual_start for completed tasks
    if "actual_start" in tasks.columns and "actual_end" in tasks.columns:
        completed = tasks[tasks["status"] == "completed"]
        if len(completed) > 0:
            # Check for valid values (not -1 which indicates missing)
            valid_completed = completed[
                (completed["actual_start"] >= 0) & 
                (completed["actual_end"] >= 0)
            ]
            if len(valid_completed) > 0:
                invalid_timing = valid_completed["actual_end"] < valid_completed["actual_start"]
                if invalid_timing.any():
                    bad_count = invalid_timing.sum()
                    errors.append(f"actual_end < actual_start for {bad_count} completed tasks")
    
    return errors


def validate_events(events: pd.DataFrame) -> List[str]:
    """
    Validates event data quality.
    
    Checks:
    - Required columns exist
    - No NaN in critical fields
    - day values are non-negative
    - event_type is valid
    - observed_day >= day (if present)
    
    Args:
        events: Event DataFrame to validate
    
    Returns:
        List of error messages (empty if valid)
    """
    errors: List[str] = []
    
    # Check required columns
    missing_cols = [col for col in REQUIRED_EVENT_COLUMNS if col not in events.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
        return errors
    
    # Check for NaN in critical fields
    for col in ["task_id", "event_type", "day"]:
        if col in events.columns and events[col].isna().any():
            nan_count = events[col].isna().sum()
            errors.append(f"Found {nan_count} NaN values in '{col}'")
    
    # Validate day is non-negative
    if (events["day"] < 0).any():
        bad_count = (events["day"] < 0).sum()
        errors.append(f"day must be non-negative ({bad_count} violations)")
    
    # Validate event_type values
    invalid_types = ~events["event_type"].isin(VALID_EVENT_TYPES)
    if invalid_types.any():
        bad_values = events.loc[invalid_types, "event_type"].unique().tolist()
        errors.append(f"Invalid event_type values: {bad_values}")
    
    # Validate observed_day >= day (if column exists)
    if "observed_day" in events.columns:
        invalid_observed = events["observed_day"] < events["day"]
        if invalid_observed.any():
            bad_count = invalid_observed.sum()
            errors.append(f"observed_day < day for {bad_count} events")
    
    return errors


def validate_features(features: pd.DataFrame) -> List[str]:
    """
    Validates feature data quality.
    
    Checks:
    - No NaN in numeric columns
    - Feature values are non-negative
    
    Args:
        features: Feature DataFrame to validate
    
    Returns:
        List of error messages (empty if valid)
    """
    errors: List[str] = []
    
    # Check for NaN in numeric columns
    numeric_cols = features.select_dtypes(include="number").columns
    for col in numeric_cols:
        if features[col].isna().any():
            nan_count = features[col].isna().sum()
            errors.append(f"Found {nan_count} NaN values in feature '{col}'")
    
    # Check for negative values in count-based features
    count_features = [
        "total_blocked_events", "dependencies", "rework_count",
        "no_resource_available", "progress_events"
    ]
    for col in count_features:
        if col in features.columns and (features[col] < 0).any():
            bad_count = (features[col] < 0).sum()
            errors.append(f"Negative values in '{col}' ({bad_count} violations)")
    
    return errors
