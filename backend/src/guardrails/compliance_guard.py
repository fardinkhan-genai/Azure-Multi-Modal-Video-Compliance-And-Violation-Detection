from typing import Literal

from pydantic import BaseModel
from guardrails import Guard


class ComplianceIssue(BaseModel):
    category: str
    severity: str
    description: str


class ComplianceResult(BaseModel):
    status: Literal["PASS", "FAIL", "REQUIRES_REVIEW"]
    compliance_results: list[ComplianceIssue]
    final_report: str


guard = Guard.for_pydantic(
    output_class=ComplianceResult
)