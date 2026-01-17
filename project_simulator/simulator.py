import random
from typing import List, Dict, Optional

from project_simulator.entities import Task, Resource, EventLog
from project_simulator.utils import chance, random_delay, regress_progress


class ProjectSimulator:
    """
    Project execution simulator with:
    - dependencies
    - resource constraints
    - skill mismatch
    - random disruptions
    - noisy / delayed logging
    """

    def __init__(
        self,
        tasks: List[Task],
        resources: List[Resource],
        seed: int = 42,
        noise_config: Optional[dict] = None
    ):
        self.tasks: Dict[str, Task] = {t.task_id: t for t in tasks}
        self.resources: List[Resource] = resources
        self.logs: List[EventLog] = []
        self.delayed_logs: List[EventLog] = []

        self.day: int = 0
        random.seed(seed)

        # -------------------------------
        # Noise configuration
        # -------------------------------
        self.noise = noise_config or {
            "disruption_prob": 0.1,
            "rework_prob": 0.05,
            "external_block_prob": 0.05,
            "log_drop_prob": 0.15,
            "log_delay_range": (1, 3),
        }

    # -------------------------------------------------
    # Dependency logic
    # -------------------------------------------------
    def dependencies_completed(self, task: Task) -> bool:
        return all(
            self.tasks[dep].status == "completed"
            for dep in task.dependencies
        )

    # -------------------------------------------------
    # Resource logic
    # -------------------------------------------------
    def find_resource_for_task(self, task: Task):
        for resource in self.resources:
            if resource.assigned_task is None:
                return resource
        return None

    def release_resources(self):
        for resource in self.resources:
            resource.assigned_task = None

    # -------------------------------------------------
    # Logging logic (with noise)
    # -------------------------------------------------
    def log_event(self, event: EventLog):
        """
        Applies log dropping and delayed logging noise.
        """
        if chance(self.noise["log_drop_prob"]):
            return  # dropped log

        if chance(0.3):  # delayed log
            delay_days = random_delay(*self.noise["log_delay_range"])
            delayed_event = EventLog(
                day=event.day + delay_days,
                task_id=event.task_id,
                event_type=event.event_type,
                reason=event.reason
            )
            self.delayed_logs.append(delayed_event)
        else:
            self.logs.append(event)

    # -------------------------------------------------
    # Simulation step
    # -------------------------------------------------
    def simulate_day(self):
        self.day += 1

        # Release delayed logs whose time has come
        ready_logs = [l for l in self.delayed_logs if l.day <= self.day]
        self.delayed_logs = [l for l in self.delayed_logs if l.day > self.day]
        self.logs.extend(ready_logs)

        for task in self.tasks.values():

            if task.status == "completed":
                continue

            # -------------------------------
            # External random block
            # -------------------------------
            if chance(self.noise["external_block_prob"]):
                task.status = "blocked"
                self.log_event(
                    EventLog(
                        self.day,
                        task.task_id,
                        "blocked",
                        "external_block"
                    )
                )
                continue

            # -------------------------------
            # Dependency block
            # -------------------------------
            if not self.dependencies_completed(task):
                task.status = "blocked"
                self.log_event(
                    EventLog(
                        self.day,
                        task.task_id,
                        "blocked",
                        "dependencies"
                    )
                )
                continue

            # -------------------------------
            # Start task (or resume from blocked)
            # -------------------------------
            if task.status == "not_started" or task.status == "blocked":
                # Transition to in_progress
                if task.status == "not_started":
                    # First time starting - set actual_start
                    if task.actual_start is None:
                        task.actual_start = self.day
                    self.log_event(
                        EventLog(self.day, task.task_id, "start")
                    )
                task.status = "in_progress"

            # -------------------------------
            # Resource allocation
            # -------------------------------
            resource = self.find_resource_for_task(task)

            if resource is None:
                task.status = "blocked"
                self.log_event(
                    EventLog(
                        self.day,
                        task.task_id,
                        "blocked",
                        "no_resource_available"
                    )
                )
                continue

            resource.assigned_task = task.task_id

            # -------------------------------
            # Skill mismatch
            # -------------------------------
            if resource.skill_type != task.required_skill:
                skill_penalty = 0.5
                reason = "skill_mismatch"
            else:
                skill_penalty = 1.0
                reason = None

            # -------------------------------
            # Random disruption
            # -------------------------------
            if chance(self.noise["disruption_prob"]):
                self.log_event(
                    EventLog(
                        self.day,
                        task.task_id,
                        "blocked",
                        "random_disruption"
                    )
                )
                continue

            # -------------------------------
            # Progress update
            # -------------------------------
            base_progress = random.uniform(0.05, 0.15)

            increment = (
                base_progress
                * resource.efficiency
                * skill_penalty
                / task.complexity
            )

            task.progress += increment

            self.log_event(
                EventLog(
                    self.day,
                    task.task_id,
                    "progress",
                    reason
                )
            )

            # -------------------------------
            # Rework (progress regression)
            # -------------------------------
            if chance(self.noise["rework_prob"]):
                task.progress = regress_progress(task.progress)
                self.log_event(
                    EventLog(
                        self.day,
                        task.task_id,
                        "rework",
                        "rework"
                    )
                )

            # -------------------------------
            # Completion
            # -------------------------------
            if task.progress >= 1.0:
                # Defensive: ensure actual_start is set
                if task.actual_start is None:
                    task.actual_start = self.day
                
                task.status = "completed"
                task.actual_end = self.day
                self.log_event(
                    EventLog(self.day, task.task_id, "complete")
                )

        self.release_resources()

    # -------------------------------------------------
    # Run loop
    # -------------------------------------------------
    def run(self, max_days: int = 120):
        for _ in range(max_days):
            self.simulate_day()

            if all(t.status == "completed" for t in self.tasks.values()):
                break
