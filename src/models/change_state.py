
"""Shared change-state model for the review workflow."""

from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict

from src.models.finding import Finding


class ReviewStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MergeRecommendation(str, Enum):
    APPROVE = "APPROVE"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class ChangeState(BaseModel):
    """Central state containing all information about a code review."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )
    
    # All relevant source and repository files.
    file_contents: dict[str, str] = Field(
        default_factory=dict,
        description="File paths mapped to their source contents",
    )

    # Test files supplied with the code change.
    test_files: dict[str, str] = Field(
        default_factory=dict,
        description="Test file paths mapped to their contents",
    )

    # Optional output from an actual coverage run.
    coverage_report: Optional[str] = Field(
        default=None,
        description="Coverage report, if available",
    )


    change_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this code review",
    )

    title: str = Field(
        default="Untitled Code Change",
        description="Name of the submitted change",
    )

    description: str = Field(
        default="",
        description="Description of the submitted change",
    )

    original_code: str = Field(
        default="",
        description="Original source code",
    )

    modified_code: str = Field(
        default="",
        description="Modified source code",
    )

    diff: str = Field(
        default="",
        description="Git diff representing the code changes",
    )

    files_changed: list[str] = Field(
        default_factory=list,
        description="List of modified files",
    )

    findings: list[Finding] = Field(
        default_factory=list,
        description="Findings collected from all review agents",
    )

    status: ReviewStatus = Field(
        default=ReviewStatus.PENDING,
        description="Current review status",
    )

    review_summary: str = Field(
        default="",
        description="Consolidated review summary",
    )

    merge_recommendation: Optional[MergeRecommendation] = Field(
        default=None,
        description="Final merge recommendation",
    )

    suggested_patch: Optional[str] = Field(
        default=None,
        description="Patch suggested by the Fix-Suggestion Agent",
    )

    errors: list[str] = Field(
        default_factory=list,
        description="Errors encountered during the review",
    )

    def add_finding(self, finding: Finding) -> None:
        """Add a finding while avoiding duplicate IDs."""

        if not any(existing.id == finding.id for existing in self.findings):
            self.findings.append(finding)

    def get_findings_by_severity(
        self,
        severity: str,
    ) -> list[Finding]:
        """Return findings matching a severity level."""

        return [
            finding
            for finding in self.findings
            if finding.severity == severity
        ]
