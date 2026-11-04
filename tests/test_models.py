
"""Tests for the shared review data models."""

from pydantic import ValidationError

from src.models import (
    Finding,
    Severity,
    ChangeState,
    ReviewStatus,
    MergeRecommendation,
)


def test_finding_creation():
    finding = Finding(
        agent_name="Security Agent",
        title="Possible SQL Injection",
        description="User input is directly concatenated into SQL.",
        severity=Severity.CRITICAL,
        file_path="app.py",
        line_number=15,
        evidence="query = 'SELECT * FROM users WHERE id=' + user_id",
        suggestion="Use parameterized SQL queries.",
    )

    assert finding.agent_name == "Security Agent"
    assert finding.severity == Severity.CRITICAL
    assert finding.line_number == 15
    assert finding.id is not None


def test_invalid_line_number():
    try:
        Finding(
            agent_name="Style Agent",
            title="Bad line number",
            description="Testing validation",
            severity=Severity.LOW,
            line_number=0,
        )
    except ValidationError:
        return

    assert False, "Expected ValidationError for line_number=0"


def test_change_state_creation():
    state = ChangeState(
        title="Add login functionality",
        description="Introduces a new login endpoint",
        files_changed=["app.py", "test_app.py"],
        status=ReviewStatus.IN_PROGRESS,
    )

    assert state.title == "Add login functionality"
    assert len(state.files_changed) == 2
    assert state.status == ReviewStatus.IN_PROGRESS
    assert state.findings == []


def test_add_finding():
    state = ChangeState()

    finding = Finding(
        agent_name="Style Agent",
        title="Missing docstring",
        description="Function is missing a docstring.",
        severity=Severity.LOW,
    )

    state.add_finding(finding)

    assert len(state.findings) == 1
    assert state.findings[0].title == "Missing docstring"


def test_duplicate_finding_id():
    state = ChangeState()

    finding = Finding(
        id="finding-001",
        agent_name="Security Agent",
        title="Hardcoded secret",
        description="A secret is hardcoded.",
        severity=Severity.HIGH,
    )

    state.add_finding(finding)
    state.add_finding(finding)

    assert len(state.findings) == 1


def test_filter_by_severity():
    state = ChangeState()

    critical = Finding(
        agent_name="Security Agent",
        title="Critical vulnerability",
        description="Test finding",
        severity=Severity.CRITICAL,
    )

    low = Finding(
        agent_name="Style Agent",
        title="Naming issue",
        description="Test finding",
        severity=Severity.LOW,
    )

    state.add_finding(critical)
    state.add_finding(low)

    results = state.get_findings_by_severity("CRITICAL")

    assert len(results) == 1
    assert results[0].title == "Critical vulnerability"


def test_merge_recommendation():
    state = ChangeState(
        merge_recommendation=MergeRecommendation.REQUEST_CHANGES
    )

    assert (
        state.merge_recommendation
        == MergeRecommendation.REQUEST_CHANGES
    )

def test_add_finding():
    """A new finding should be added to ChangeState."""

    from src.models.change_state import ChangeState
    from src.models.finding import Finding, Severity

    state = ChangeState(
        change_id="test-001",
        title="Test Change",
        description="Testing finding addition",
        original_code="",
        modified_code="",
        diff="",
        files_changed=[],
    )

    finding = Finding(
        id="finding-001",
        agent_name="Security Agent",
        title="SQL Injection",
        description="Unsafe SQL query.",
        severity=Severity.CRITICAL,
    )

    state.add_finding(finding)

    assert len(state.findings) == 1
    assert state.findings[0].id == finding.id


def test_add_duplicate_finding():
    """A finding with an existing ID should not be added twice."""

    from src.models.change_state import ChangeState
    from src.models.finding import Finding, Severity

    state = ChangeState(
        change_id="test-002",
        title="Test Change",
        description="Testing duplicate findings",
        original_code="",
        modified_code="",
        diff="",
        files_changed=[],
    )

    finding = Finding(
        id="finding-002",
        agent_name="Security Agent",
        title="SQL Injection",
        description="Unsafe SQL query.",
        severity=Severity.CRITICAL,
    )

    state.add_finding(finding)
    state.add_finding(finding)

    assert len(state.findings) == 1


def test_different_finding_ids_are_accepted():
    """Different finding IDs should be accepted."""

    from src.models.change_state import ChangeState
    from src.models.finding import Finding, Severity

    state = ChangeState(
        change_id="test-003",
        title="Test Change",
        description="Testing distinct findings",
        original_code="",
        modified_code="",
        diff="",
        files_changed=[],
    )

    finding1 = Finding(
        id="finding-003",
        agent_name="Security Agent",
        title="SQL Injection",
        description="Unsafe SQL query.",
        severity=Severity.CRITICAL,
    )

    finding2 = Finding(
        id="finding-004",
        agent_name="Diff Agent",
        title="SQL Injection",
        description="Another observation.",
        severity=Severity.HIGH,
    )

    state.add_finding(finding1)
    state.add_finding(finding2)

    assert len(state.findings) == 2

def test_get_findings_by_severity():
    """Only findings with the requested severity should be returned."""

    from src.models.change_state import ChangeState
    from src.models.finding import Finding, Severity

    state = ChangeState()

    findings = [
        Finding(
            id="severity-001",
            agent_name="Security Agent",
            title="SQL Injection",
            description="Critical vulnerability.",
            severity=Severity.CRITICAL,
        ),
        Finding(
            id="severity-002",
            agent_name="Style Agent",
            title="Poor Naming",
            description="Naming could be improved.",
            severity=Severity.LOW,
        ),
        Finding(
            id="severity-003",
            agent_name="Diff Agent",
            title="Missing Validation",
            description="Validation is missing.",
            severity=Severity.HIGH,
        ),
    ]

    for finding in findings:
        state.add_finding(finding)

    critical_findings = state.get_findings_by_severity(Severity.CRITICAL)

    assert len(critical_findings) == 1
    assert critical_findings[0].title == "SQL Injection"


def test_get_findings_by_severity_multiple_matches():
    """Multiple findings with the same severity should be returned."""

    from src.models.change_state import ChangeState
    from src.models.finding import Finding, Severity

    state = ChangeState()

    for i in range(3):
        state.add_finding(
            Finding(
                id=f"medium-{i}",
                agent_name="Test Agent",
                title=f"Medium Issue {i}",
                description="A medium severity issue.",
                severity=Severity.MEDIUM,
            )
        )

    results = state.get_findings_by_severity(Severity.MEDIUM)

    assert len(results) == 3
    assert all(f.severity == Severity.MEDIUM for f in results)


def test_get_findings_by_severity_no_matches():
    """An empty list should be returned when no severity matches."""

    from src.models.change_state import ChangeState
    from src.models.finding import Finding, Severity

    state = ChangeState()

    state.add_finding(
        Finding(
            id="low-001",
            agent_name="Style Agent",
            title="Minor Style Issue",
            description="A minor formatting issue.",
            severity=Severity.LOW,
        )
    )

    results = state.get_findings_by_severity(Severity.CRITICAL)

    assert results == []
