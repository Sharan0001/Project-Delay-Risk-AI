"""
Pydantic Schemas for FastAPI Request/Response Models.

Defines the API contract for the Project Delay Risk AI system.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request body for /analyze endpoint."""
    what_if: Optional[str] = Field(
        None,
        description="What-if scenario to analyze",
        json_schema_extra={"example": "add_resource"}
    )


class WhatIfImpact(BaseModel):
    """Impact of a what-if scenario on task risk."""
    scenario: Optional[str] = Field(None, description="Scenario that was applied")
    new_delay_probability: float = Field(..., ge=0, le=1, description="New probability after scenario")
    probability_reduction: Optional[float] = Field(None, description="Change in probability")


class TaskRiskResponse(BaseModel):
    """Risk assessment for a single task."""
    task_id: str = Field(..., description="Task identifier")
    risk_level: Literal["High", "Medium", "Low"] = Field(..., description="Risk classification")
    risk_score: int = Field(..., ge=0, le=100, description="Numeric risk score")
    delay_probability: float = Field(..., ge=0, le=1, description="ML-predicted probability")
    reasons: List[str] = Field(default_factory=list, description="Triggered risk rules")
    recommended_actions: List[str] = Field(default_factory=list, description="Suggested actions")
    what_if_impact: Optional[WhatIfImpact] = Field(None, description="Scenario impact if requested")


class AnalyzeResponse(BaseModel):
    """Response from /analyze endpoint."""
    results: List[TaskRiskResponse] = Field(..., description="Risk assessments for all tasks")
