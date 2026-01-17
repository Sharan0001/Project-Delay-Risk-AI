import pandas as pd


# -------------------------------------------------
# Blocking-related features
# -------------------------------------------------
def compute_block_features(events: pd.DataFrame) -> pd.DataFrame:
    """
    Computes blocking-related metrics per task.
    """
    blocked = events[events["event_type"] == "blocked"]

    block_counts = (
        blocked.groupby(["task_id", "reason"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    # Ensure consistent columns
    for col in [
        "dependencies",
        "no_resource_available",
        "skill_mismatch",
        "external_block",
        "random_disruption",
    ]:
        if col not in block_counts.columns:
            block_counts[col] = 0

    block_counts["total_blocked_events"] = (
        block_counts[
            [
                "dependencies",
                "no_resource_available",
                "skill_mismatch",
                "external_block",
                "random_disruption",
            ]
        ].sum(axis=1)
    )

    return block_counts


# -------------------------------------------------
# Progress & rework features
# -------------------------------------------------
def compute_progress_features(events: pd.DataFrame) -> pd.DataFrame:
    """
    Computes progress instability and rework signals.
    """
    progress = events[events["event_type"] == "progress"]
    rework = events[events["event_type"] == "rework"]

    progress_stats = (
        progress.groupby("task_id")["day"]
        .agg(
            progress_events="count",
            first_progress_day="min",
            last_progress_day="max",
        )
        .reset_index()
    )

    rework_counts = (
        rework.groupby("task_id")
        .size()
        .reset_index(name="rework_count")
    )

    features = progress_stats.merge(
        rework_counts, on="task_id", how="left"
    )
    features["rework_count"] = features["rework_count"].fillna(0)

    return features


# -------------------------------------------------
# Temporal stagnation features
# -------------------------------------------------
def compute_stagnation_features(events: pd.DataFrame) -> pd.DataFrame:
    """
    Measures inactivity gaps between progress events.
    """
    progress = events[events["event_type"] == "progress"]

    gaps = []
    for task_id, group in progress.groupby("task_id"):
        days = sorted(group["day"].tolist())
        if len(days) <= 1:
            max_gap = 0
        else:
            max_gap = max(
                days[i + 1] - days[i]
                for i in range(len(days) - 1)
            )
        gaps.append({
            "task_id": task_id,
            "max_progress_gap": max_gap
        })

    return pd.DataFrame(gaps)


# -------------------------------------------------
# Master feature builder
# -------------------------------------------------
def build_task_features(tasks: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """
    Combines all task-level features into one table.
    """
    block_features = compute_block_features(events)
    progress_features = compute_progress_features(events)
    stagnation_features = compute_stagnation_features(events)

    features = tasks.merge(block_features, on="task_id", how="left")
    features = features.merge(progress_features, on="task_id", how="left")
    features = features.merge(stagnation_features, on="task_id", how="left")

    # Fill missing numeric values
    numeric_cols = features.select_dtypes(include="number").columns
    features[numeric_cols] = features[numeric_cols].fillna(0)

    return features
