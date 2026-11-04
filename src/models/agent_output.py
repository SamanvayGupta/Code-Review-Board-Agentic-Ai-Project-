
"""Standardized output returned by every review agent."""

from pydantic import BaseModel, Field

from src.models.finding import Finding


class AgentReviewOutput(BaseModel):
    """Validated response from an individual review agent."""

    agent_name: str = Field(
        description="Name of the reviewing agent"
    )

    summary: str = Field(
        description="Short summary of the agent's analysis"
    )

    findings: list[Finding] = Field(
        default_factory=list,
        description="Issues discovered by this agent"
    )
