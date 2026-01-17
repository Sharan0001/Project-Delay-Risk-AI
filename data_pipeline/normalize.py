"""
Data normalization module for the Project Delay Risk AI system.

Handles cleaning and standardizing raw simulation data:
- Normalizes event timestamps (handles delayed logging)
- Computes derived task fields (delay labels)
"""

import pandas as pd
from typing import Tuple


def normalize_events(events: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes event timestamps and flags delayed logs.
    
    In real project environments, logs often arrive late due to:
    - Manual entry delays
    - System synchronization issues
    - Batched updates
    
    This function:
    1. Identifies delayed log entries (where observed_day > day)
    2. Flags events for analysis
    3. Sorts by observed_day for temporal analysis
    
    Note: The simulator already handles delayed logging by setting
    observed_day during event creation. This function simply flags
    and sorts the data.
    
    Args:
        events: Raw event DataFrame with 'day', 'observed_day', 'event_type' columns
        
    Returns:
        Normalized DataFrame sorted by observed_day
    """
    events = events.copy()

    # Flag delayed logs (where observed_day > actual day)
    # This can happen due to batched updates or system delays
    events["is_delayed_log"] = events["observed_day"] > events["day"]

    return events.sort_values("observed_day").reset_index(drop=True)


def normalize_tasks(tasks: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes task-level fields and computes delay labels.
    
    Delay Logic:
    - A task is marked as delayed if its actual duration exceeds planned duration
    - actual_duration = actual_end - actual_start
    - delay = 1 if actual_duration > planned_duration, else 0
    
    Edge Cases:
    - Tasks without actual_end (incomplete): marked with actual_end = -1
    - Tasks without actual_start: cannot compute delay, marked as not delayed
    
    Args:
        tasks: Raw task DataFrame with scheduling fields
        
    Returns:
        Normalized DataFrame with 'delay' column added
    """
    tasks = tasks.copy()

    # Missing actual_end means unfinished or logging failure
    tasks["actual_end"] = tasks["actual_end"].fillna(-1)
    
    # Missing actual_start means task never started
    tasks["actual_start"] = tasks["actual_start"].fillna(-1)

    # Delay computation:
    # A task is delayed if it took longer than planned
    # We can only compute this for completed tasks (actual_end > 0 and actual_start > 0)
    def compute_delay(row) -> int:
        """
        Determines if a task was delayed.
        
        Returns:
            1 if task took longer than planned, 0 otherwise
        """
        if row["actual_end"] < 0 or row["actual_start"] < 0:
            # Incomplete task or missing data - cannot determine delay
            # Default to 0 (not delayed) to avoid false positives
            return 0
        
        actual_duration = row["actual_end"] - row["actual_start"]
        return 1 if actual_duration > row["planned_duration"] else 0
    
    tasks["delay"] = tasks.apply(compute_delay, axis=1)

    return tasks
