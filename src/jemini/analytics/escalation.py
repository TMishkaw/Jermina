"""Agent self-improvement and feature gap escalation engine."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class FeatureGapReport(BaseModel):
    id: str
    channel_id: str
    missing_capability: str
    impact_description: str
    suggested_solution: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    github_issue_url: str | None = None

class EscalationManager:
    """Detects unfulfilled capabilities during daily workflows and prepares GitHub Issues / PR proposals."""

    def __init__(self):
        self.reports: list[FeatureGapReport] = []

    def record_feature_gap(
        self,
        channel_id: str,
        missing_capability: str,
        impact: str,
        suggestion: str,
    ) -> FeatureGapReport:
        report = FeatureGapReport(
            id=f"gap_{len(self.reports) + 1}",
            channel_id=channel_id,
            missing_capability=missing_capability,
            impact_description=impact,
            suggested_solution=suggestion,
        )
        self.reports.append(report)
        return report

    def format_github_issue_body(self, report: FeatureGapReport) -> str:
        return (
            f"### [Autonomous Escalation] Feature Gap Detected\n\n"
            f"- **Channel ID**: `{report.channel_id}`\n"
            f"- **Missing Capability**: {report.missing_capability}\n"
            f"- **Impact**: {report.impact_description}\n\n"
            f"#### Suggested Solution / PR Plan:\n"
            f"{report.suggested_solution}\n\n"
            f"*Generated autonomously by Jemini Agent Evolution Loop.*"
        )
