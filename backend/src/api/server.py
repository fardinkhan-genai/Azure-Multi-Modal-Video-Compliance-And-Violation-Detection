import logging
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langsmith import Client, tracing_context

from backend.src.api.telemetry import setup_telemetry
from backend.src.graph.workflow import app as compliance_graph


# Load existing .env variables
load_dotenv(override=True)


# Start Azure Monitor / Application Insights
setup_telemetry()


# LangSmith client
langsmith_client = Client(
    api_url=os.getenv("LANGCHAIN_ENDPOINT"),
    api_key=os.getenv("LANGCHAIN_API_KEY"),
)


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(
    "azure-multimodal-compliance"
)


app = FastAPI(
    title="Azure Multi-Modal Video Compliance & Violation Detection",
    description="Video compliance checking with Azure AI and LangGraph.",
    version="1.0.0",
)


# Frontend
PROJECT_ROOT = Path(__file__).resolve().parents[3]

FRONTEND_FOLDER = PROJECT_ROOT / "frontend"

app.mount(
    "/frontend",
    StaticFiles(directory=FRONTEND_FOLDER),
    name="frontend",
)


class AuditRequest(BaseModel):
    video_url: str


class ComplianceIssue(BaseModel):
    category: str
    severity: str
    description: str


class AuditResponse(BaseModel):
    session_id: str
    video_id: str
    status: str
    final_report: str
    compliance_results: list[ComplianceIssue]


@app.get("/")
def home():
    return FileResponse(
        FRONTEND_FOLDER / "index.html"
    )


@app.post(
    "/audit",
    response_model=AuditResponse
)
def audit_video(request: AuditRequest):

    session_id = str(uuid.uuid4())

    video_id = f"vid_{session_id[:8]}"

    inputs = {
        "video_url": request.video_url,
        "video_id": video_id,
        "compliance_results": [],
        "errors": [],
    }

    logger.info(
        "Starting audit %s",
        session_id
    )

    try:

        # Send the complete LangGraph execution to LangSmith
        with tracing_context(
            client=langsmith_client,
            project_name=os.getenv(
                "LANGCHAIN_PROJECT"
            ),
            name="video-compliance-audit",
            tags=[
                "azure",
                "video-compliance",
                "langgraph",
            ],
            metadata={
                "session_id": session_id,
                "video_id": video_id,
            },
        ):

            result = compliance_graph.invoke(
                inputs
            )

        logger.info(
            "Audit completed %s",
            session_id
        )

        return AuditResponse(
            session_id=session_id,
            video_id=result.get(
                "video_id",
                video_id
            ),
            status=result.get(
                "final_status",
                "UNKNOWN"
            ),
            final_report=result.get(
                "final_report",
                "No report generated."
            ),
            compliance_results=result.get(
                "compliance_results",
                []
            ),
        )

    except Exception as error:

        logger.exception(
            "Audit failed"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Workflow Execution Failed: {error}",
        )


@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": (
            "Azure Multi-Modal Video "
            "Compliance & Violation Detection"
        ),
    }