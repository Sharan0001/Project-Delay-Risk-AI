"""
Data Schema Definitions.

Pydantic models for type-safe data validation and documentation.
These models define the expected structure of task and event data.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class TaskRecord(BaseModel):
    """Schema for a single task record."""
    
    task_id: str = Field(..., description="Unique task identifier")
    planned_duration: int = Field(..., gt=0, description="Expected duration in days")
    complexity: int = Field(..., ge=1, le=5, description="Difficulty factor (1-5)")
    priority: Literal["high", "medium", "low"] = Field(..., description="Task priority")
    required_skill: str = Field(..., description="Required skill type")
    num_dependencies: int = Field(..., ge=0, description="Number of dependencies")
    actual_start: Optional[int] = Field(None, description="Day when task started")
    actual_end: Optional[int] = Field(None, description="Day when task completed")
    status: Literal["not_started", "in_progress", "blocked", "completed"] = Field(
        ..., description="Current task status"
    )
    progress: float = Field(..., ge=0, le=1.5, description="Completion percentage")


class EventRecord(BaseModel):
    """Schema for a single event record."""
    
    day: int = Field(..., ge=0, description="Simulation day")
    task_id: str = Field(..., description="Associated task ID")
    event_type: Literal["start", "progress", "blocked", "rework", "complete"] = Field(
        ..., description="Type of event"
    )
    reason: Optional[str] = Field(None, description="Event reason/explanation")
    observed_day: int = Field(..., ge=0, description="Day event was observed")
    is_delayed_log: bool = Field(False, description="Whether log was delayed")


class FeatureRecord(BaseModel):
    """Schema for a single feature record."""
    
    task_id: str
    planned_duration: int
    
    # Block features
    dependencies: int = Field(..., ge=0)
    no_resource_available: int = Field(..., ge=0)
    skill_mismatch: int = Field(..., ge=0)
    external_block: int = Field(..., ge=0)
    random_disruption: int = Field(..., ge=0)
    total_blocked_events: int = Field(..., ge=0)
    
    # Progress features
    progress_events: int = Field(..., ge=0)
    first_progress_day: Optional[int] = None
    last_progress_day: Optional[int] = None
    rework_count: int = Field(..., ge=0)
    
    # Stagnation features
    max_progress_gap: int = Field(..., ge=0)


# Column lists for backward compatibility
TASK_COLUMNS = list(TaskRecord.model_fields.keys())
EVENT_COLUMNS = list(EventRecord.model_fields.keys())
