from typing import Annotated, Any, Optional, TypedDict
import operator


class ComplianceIssue(TypedDict):
    category: str
    description: str
    severity: str
    timestamp: Optional[str]


class VideoAuditState(TypedDict):
    # Input
    video_url: str
    video_id: str

    # Video information
    local_file_path: Optional[str]
    video_metadata: dict[str, Any]
    transcript: Optional[str]
    ocr_text: list[str]

    # Audit result
    compliance_results: Annotated[list[ComplianceIssue], operator.add]
    final_status: str
    final_report: str

    # Errors
    errors: Annotated[list[str], operator.add]
