
"""Structured finding model shared by all review agents."""

from enum import Enum
from uuid import uuid4
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class Finding(BaseModel):
    """A single issue discovered during code review."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique finding identifier",
    )

    agent_name: str = Field(
        description="Name of the agent that discovered the issue",
        min_length=1,
    )

    title: str = Field(
        description="Short title describing the issue",
        min_length=1,
    )

    description: str = Field(
        description="Detailed explanation of the issue",
        min_length=1,
    )

    severity: Severity = Field(
        description="Priority level of the finding",
    )

    file_path: Optional[str] = Field(
        default=None,
        description="Path of the affected file",
    )

    line_number: Optional[int] = Field(
        default=None,
        ge=1,
        description="Line number where the issue occurs",
    )

    evidence: str = Field(
        default="",
        description="Code or other evidence supporting the finding",
    )

    suggestion: str = Field(
        default="",
        description="Recommended action to fix the issue",
    )

    rule_id: Optional[str] = Field(
        default=None,
        description="Static-analysis rule identifier, if applicable",
    )
