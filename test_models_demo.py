
from src.models import (
    ChangeState,
    Finding,
    Severity,
    ReviewStatus,
    MergeRecommendation,
)

# Create a code review
state = ChangeState(
    title="Add user authentication",
    description="New authentication functionality",
    files_changed=["auth.py", "database.py"],
    status=ReviewStatus.IN_PROGRESS,
)

# Simulate a Security Agent finding
security_finding = Finding(
    agent_name="Security Agent",
    title="Hardcoded database password",
    description="Database credentials are stored directly in source code.",
    severity=Severity.CRITICAL,
    file_path="database.py",
    line_number=12,
    evidence='password = "admin123"',
    suggestion="Load credentials from environment variables.",
)

# Simulate a Style Agent finding
style_finding = Finding(
    agent_name="Style Agent",
    title="Missing function docstring",
    description="The function does not explain its purpose.",
    severity=Severity.LOW,
    file_path="auth.py",
    line_number=5,
    suggestion="Add a descriptive docstring.",
)

# Collect findings
state.add_finding(security_finding)
state.add_finding(style_finding)

# Simulate the manager's decision
state.merge_recommendation = MergeRecommendation.REQUEST_CHANGES
state.review_summary = "A critical security issue must be fixed."

# Display results
print("CHANGE ID:", state.change_id)
print("PROJECT:", state.title)
print("FILES:", state.files_changed)

print("\nFINDINGS:")

for finding in state.findings:
    print(
        f"\n[{finding.severity}] "
        f"{finding.agent_name}: {finding.title}"
    )
    print("File:", finding.file_path)
    print("Suggestion:", finding.suggestion)

print("\nFINAL DECISION:", state.merge_recommendation)
print("\nJSON OUTPUT:")
print(state.model_dump_json(indent=2))
