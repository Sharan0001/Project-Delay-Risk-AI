"""
Data Pipeline: Raw Tables Builder.

Orchestrates the complete data generation and preprocessing pipeline:
1. Generates synthetic project data via simulation
2. Ingests raw data from simulator
3. Normalizes timestamps and computes delay labels
4. Validates data quality
5. Engineers features for ML models

The simulation is designed to produce realistic, varied data for
meaningful ML training and testing.
"""

import random
import pandas as pd
from typing import Tuple, List, Optional

from data_pipeline.ingest import ingest_simulation
from data_pipeline.normalize import normalize_tasks, normalize_events
from data_pipeline.features import build_task_features
from project_simulator.simulator import ProjectSimulator
from project_simulator.entities import Task, Resource
from data_pipeline.validate import validate_tasks, validate_events


def generate_sample_project(
    num_tasks: int = 50,
    num_resources: int = 8,
    seed: int = 42
) -> Tuple[List[Task], List[Resource]]:
    """
    Generates a realistic project with varied tasks and resources.
    
    Creates tasks with:
    - Varied complexity (1-5)
    - Different priorities (high, medium, low)
    - Multiple skill types (dev, qa, ops, design)
    - Realistic dependency chains (no circular deps)
    
    Args:
        num_tasks: Number of tasks to generate (default 50)
        num_resources: Number of resources to generate (default 8)
        seed: Random seed for reproducibility
    
    Returns:
        Tuple of (tasks list, resources list)
    """
    random.seed(seed)
    
    skills = ["dev", "qa", "ops", "design"]
    priorities = ["high", "medium", "low"]
    
    # Generate resources with varied skills
    resources = []
    for i in range(num_resources):
        skill = skills[i % len(skills)]
        efficiency = round(random.uniform(0.7, 1.3), 2)
        resources.append(
            Resource(f"R{i+1}", skill, efficiency)
        )
    
    # Generate tasks with varied characteristics
    tasks = []
    for i in range(num_tasks):
        task_id = f"T{i+1}"
        
        # Vary duration based on complexity
        complexity = random.randint(1, 5)
        planned_duration = complexity + random.randint(2, 8)
        
        # Assign priority with realistic distribution
        # 20% high, 50% medium, 30% low
        priority_roll = random.random()
        if priority_roll < 0.2:
            priority = "high"
        elif priority_roll < 0.7:
            priority = "medium"
        else:
            priority = "low"
        
        # Assign skill (weighted toward dev)
        skill_roll = random.random()
        if skill_roll < 0.5:
            required_skill = "dev"
        elif skill_roll < 0.75:
            required_skill = "qa"
        elif skill_roll < 0.9:
            required_skill = "ops"
        else:
            required_skill = "design"
        
        # Create dependencies (only on earlier tasks, max 3)
        dependencies = []
        if i > 0:
            # 70% chance of having at least one dependency
            if random.random() < 0.7:
                num_deps = random.randint(1, min(3, i))
                # Only depend on tasks that exist (earlier in list)
                possible_deps = list(range(max(0, i - 10), i))
                if possible_deps:
                    dep_indices = random.sample(
                        possible_deps, 
                        min(num_deps, len(possible_deps))
                    )
                    dependencies = [f"T{idx+1}" for idx in dep_indices]
        
        tasks.append(Task(
            task_id=task_id,
            planned_duration=planned_duration,
            complexity=complexity,
            priority=priority,
            required_skill=required_skill,
            dependencies=dependencies
        ))
    
    return tasks, resources


def build_raw_tables(
    num_tasks: int = 50,
    num_resources: int = 8,
    seed: int = 42,
    max_days: int = 200
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Builds complete data tables from simulation.
    
    This is the main entry point for the data pipeline. It:
    1. Generates a sample project with realistic tasks and resources
    2. Runs the simulation
    3. Ingests, normalizes, and validates the data
    4. Engineers features for ML models
    
    Args:
        num_tasks: Number of tasks to simulate (default 50)
        num_resources: Number of resources (default 8)
        seed: Random seed for reproducibility
        max_days: Maximum simulation days
    
    Returns:
        Tuple of (task_df, event_df, feature_df)
    
    Raises:
        ValueError: If data validation fails
    """
    # Generate sample project
    tasks, resources = generate_sample_project(
        num_tasks=num_tasks,
        num_resources=num_resources,
        seed=seed
    )

    # Run simulation
    sim = ProjectSimulator(tasks, resources, seed=seed)
    sim.run(max_days=max_days)

    # Ingest raw data
    raw = ingest_simulation(sim)

    task_df = pd.DataFrame(raw["tasks"])
    event_df = pd.DataFrame(raw["events"])

    # Normalize
    task_df = normalize_tasks(task_df)
    event_df = normalize_events(event_df)
    
    # Validate
    task_errors = validate_tasks(task_df)
    event_errors = validate_events(event_df)

    if task_errors or event_errors:
        all_errors = task_errors + event_errors
        raise ValueError(f"Data validation failed: {all_errors}")

    # Feature engineering
    feature_df = build_task_features(task_df, event_df)

    return task_df, event_df, feature_df


if __name__ == "__main__":
    tasks, events, features = build_raw_tables()

    print("\n--- TASKS ---")
    print(f"Total tasks: {len(tasks)}")
    print(f"Completed: {len(tasks[tasks['status'] == 'completed'])}")
    print(f"Delayed: {tasks['delay'].sum()}")
    print(tasks.head(10))

    print("\n--- EVENTS ---")
    print(f"Total events: {len(events)}")
    print(events.head(10))

    print("\n--- FEATURES ---")
    print(f"Total features: {len(features.columns)}")
    print(features.head(10))
    
    print("\n--- FEATURE STATISTICS ---")
    print(features[["total_blocked_events", "dependencies", "rework_count", "max_progress_gap"]].describe())
