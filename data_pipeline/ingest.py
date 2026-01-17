from typing import List, Dict
from project_simulator.simulator import ProjectSimulator


def ingest_simulation(simulator: ProjectSimulator) -> Dict[str, List[dict]]:
    """
    Extracts raw task and event data from the simulator.
    No cleaning. No assumptions.
    """

    # -----------------------
    # Tasks
    # -----------------------
    tasks = []
    for task in simulator.tasks.values():
        tasks.append({
            "task_id": task.task_id,
            "planned_duration": task.planned_duration,
            "complexity": task.complexity,
            "priority": task.priority,
            "required_skill": task.required_skill,
            "num_dependencies": len(task.dependencies),
            "actual_start": task.actual_start,
            "actual_end": task.actual_end,
            "status": task.status,
            "progress": task.progress
        })

    # -----------------------
    # Events
    # -----------------------
    events = []
    for event in simulator.logs:
        events.append({
            "day": event.day,
            "task_id": event.task_id,
            "event_type": event.event_type,
            "reason": event.reason,
            "observed_day": event.day,      # will change in normalization
            "is_delayed_log": False
        })

    return {
        "tasks": tasks,
        "events": events
    }
