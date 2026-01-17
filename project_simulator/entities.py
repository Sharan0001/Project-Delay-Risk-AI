"""
Entity definitions for the Project Delay Risk AI simulation system.

These dataclasses represent the core domain objects:
- Task: A unit of work with scheduling, complexity, and dependency info
- Resource: A team member or asset that can be assigned to tasks
- EventLog: A timestamped record of simulation events

Design Principles:
- Validation at construction time prevents invalid states
- Enums provide type safety for categorical fields
- Clear separation between planning state and execution state
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class TaskStatus(Enum):
    """Valid task states in the simulation."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"


class Priority(Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EventType(Enum):
    """Valid event types for logging."""
    START = "start"
    PROGRESS = "progress"
    BLOCKED = "blocked"
    REWORK = "rework"
    COMPLETE = "complete"


# Valid skill types in the system
VALID_SKILLS = {"dev", "qa", "ops", "design", "pm"}


@dataclass
class Task:
    """
    Represents a project task with planning and execution state.
    
    Attributes:
        task_id: Unique identifier for the task
        planned_duration: Expected duration in days (must be > 0)
        complexity: Difficulty factor (1-5 scale, higher = more complex)
        priority: Task priority level ("high", "medium", "low")
        required_skill: Skill type needed to perform task
        dependencies: List of task_ids that must complete before this task
        actual_start: Day when task actually started (None if not started)
        actual_end: Day when task completed (None if not completed)
        progress: Completion percentage (0.0 to 1.0)
        status: Current state (TaskStatus enum or string for backwards compatibility)
    
    Raises:
        ValueError: If validation fails on any field
    """
    task_id: str
    planned_duration: int
    complexity: int
    priority: str
    required_skill: str
    dependencies: List[str] = field(default_factory=list)

    actual_start: Optional[int] = None
    actual_end: Optional[int] = None
    progress: float = 0.0
    status: str = "not_started"
    
    def __post_init__(self):
        """Validates task fields after initialization."""
        # Validate task_id
        if not self.task_id or not isinstance(self.task_id, str):
            raise ValueError(f"task_id must be a non-empty string, got: {self.task_id}")
        
        # Validate planned_duration
        if self.planned_duration <= 0:
            raise ValueError(f"planned_duration must be positive, got: {self.planned_duration}")
        
        # Validate complexity (1-5 scale)
        if not (1 <= self.complexity <= 5):
            raise ValueError(f"complexity must be between 1 and 5, got: {self.complexity}")
        
        # Validate priority
        valid_priorities = {p.value for p in Priority}
        if self.priority not in valid_priorities:
            raise ValueError(f"priority must be one of {valid_priorities}, got: {self.priority}")
        
        # Validate progress range
        if not (0.0 <= self.progress <= 1.5):  # Allow slight overshoot
            raise ValueError(f"progress must be between 0.0 and 1.5, got: {self.progress}")
        
        # Validate status
        valid_statuses = {s.value for s in TaskStatus}
        if self.status not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}, got: {self.status}")
    
    def is_completed(self) -> bool:
        """Returns True if task is completed."""
        return self.status == TaskStatus.COMPLETED.value
    
    def is_blocked(self) -> bool:
        """Returns True if task is blocked."""
        return self.status == TaskStatus.BLOCKED.value
    
    def can_start(self) -> bool:
        """Returns True if task hasn't started yet."""
        return self.status == TaskStatus.NOT_STARTED.value


@dataclass
class Resource:
    """
    Represents a resource (person or asset) that can work on tasks.
    
    Attributes:
        resource_id: Unique identifier for the resource
        skill_type: Primary skill ("dev", "qa", "ops", "design", "pm")
        efficiency: Work rate multiplier (must be > 0, 1.0 = normal)
        availability: Hours available per day (must be > 0, default 8)
        assigned_task: Currently assigned task_id (None if idle)
    
    Raises:
        ValueError: If validation fails on any field
    """
    resource_id: str
    skill_type: str
    efficiency: float
    availability: int = 8
    assigned_task: Optional[str] = None
    
    def __post_init__(self):
        """Validates resource fields after initialization."""
        # Validate resource_id
        if not self.resource_id or not isinstance(self.resource_id, str):
            raise ValueError(f"resource_id must be a non-empty string, got: {self.resource_id}")
        
        # Validate efficiency
        if self.efficiency <= 0:
            raise ValueError(f"efficiency must be positive, got: {self.efficiency}")
        
        # Validate availability
        if self.availability <= 0:
            raise ValueError(f"availability must be positive, got: {self.availability}")
    
    def is_available(self) -> bool:
        """Returns True if resource is not assigned to any task."""
        return self.assigned_task is None
    
    def assign(self, task_id: str) -> None:
        """Assigns resource to a task."""
        self.assigned_task = task_id
    
    def release(self) -> None:
        """Releases resource from current task."""
        self.assigned_task = None


@dataclass
class EventLog:
    """
    Immutable record of a simulation event.
    
    Attributes:
        day: Simulation day when event occurred (must be >= 0)
        task_id: Task associated with this event
        event_type: Type of event ("start", "progress", "blocked", "rework", "complete")
        reason: Optional explanation (e.g., "dependencies", "no_resource_available")
    
    Raises:
        ValueError: If validation fails on any field
    """
    day: int
    task_id: str
    event_type: str
    reason: Optional[str] = None
    
    def __post_init__(self):
        """Validates event fields after initialization."""
        # Validate day
        if self.day < 0:
            raise ValueError(f"day must be non-negative, got: {self.day}")
        
        # Validate task_id
        if not self.task_id or not isinstance(self.task_id, str):
            raise ValueError(f"task_id must be a non-empty string, got: {self.task_id}")
        
        # Validate event_type
        valid_types = {e.value for e in EventType}
        if self.event_type not in valid_types:
            raise ValueError(f"event_type must be one of {valid_types}, got: {self.event_type}")

