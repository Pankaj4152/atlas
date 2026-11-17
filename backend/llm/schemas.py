"""
Pydantic schemas for structured LLM inputs and outputs.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class AnomalyContext(BaseModel):
    """Data payload compiled by the pipeline and fed into the LLM."""
    incident_id: str
    time_window: str
    severity_hint: str
    total_logs: int
    error_count: int
    critical_count: int
    warning_count: int
    detector_summary: str
    top_templates: List[str]
    sample_raw_logs: List[str]


class LLMAnalysisResult(BaseModel):
    """Structured, validated response returned by the LLM."""
    title: str = Field(description="Short, descriptive title of the incident")
    severity: Literal["critical", "high", "medium", "low"] = Field(
        description="Assessed severity level"
    )
    probable_root_cause: str = Field(
        description="The most probable technical cause based on log evidence"
    )
    confidence: Literal["high", "medium", "low"] = Field(
        description="Confidence in the diagnosed root cause"
    )
    explanation: str = Field(
        description="Clear, human-readable summary of what happened"
    )
    recommended_actions: List[str] = Field(
        description="Concrete, actionable troubleshooting steps"
    )
