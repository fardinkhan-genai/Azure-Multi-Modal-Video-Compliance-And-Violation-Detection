import json
import logging
import os
import re

from langchain_community.vectorstores import AzureSearch
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from backend.src.graph.state import VideoAuditState
from backend.src.services.video_indexer import VideoIndexerService

logger = logging.getLogger("azure-multimodal-compliance")


def index_video_node(state: VideoAuditState):
    """Download the video, send it to Azure Video Indexer, and get transcript/OCR."""
    video_url = state.get("video_url", "")
    video_id = state.get("video_id", "vid_demo")
    local_path = "temp_audit_video.mp4"

    try:
        service = VideoIndexerService()

        # 1. DOWNLOAD
        if "youtube.com" not in video_url and "youtu.be" not in video_url:
            raise Exception("Please provide a valid YouTube URL for this test.")

        service.download_youtube_video(video_url, local_path)

        # 2. UPLOAD
        azure_video_id = service.upload_video(local_path, video_id)
        logger.info("Video uploaded to Azure Video Indexer: %s", azure_video_id)

        # 3. CLEANUP
        if os.path.exists(local_path):
            os.remove(local_path)

        # 4. WAIT
        raw_data = service.wait_for_processing(azure_video_id)

        # 5. EXTRACT
        return service.extract_data(raw_data)

    except Exception as error:
        logger.error("Video Indexer failed: %s", error)
        if os.path.exists(local_path):
            os.remove(local_path)

        return {
            "errors": [str(error)],
            "final_status": "FAIL",
            "transcript": "",
            "ocr_text": [],
        }


def audit_content_node(state: VideoAuditState):
    """Find the relevant rules and ask Azure OpenAI to audit the video.
    Performs Retrieval-Augmented Generation (RAG) to audit the content.
    """
    transcript = state.get("transcript", "")

    if not transcript:
        return {
            "final_status": "FAIL",
            "final_report": "Audit skipped because no transcript was available.",
        }

    try:
        llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0,
        )

        embeddings = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )

        vector_store = AzureSearch(
            azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"),
            index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
            embedding_function=embeddings.embed_query,
        )

        # RAG Retrieval
        ocr_text = state.get("ocr_text", [])
        query = f"{transcript} {' '.join(ocr_text)}"
        documents = vector_store.similarity_search(query, k=3)

        rules = "\n\n".join(doc.page_content for doc in documents)

        # UPDATED PROMPT WITH STRICT SCHEMA

        system_prompt = f"""
        You are a Senior Brand Compliance Auditor.

        OFFICIAL REGULATORY RULES:
        {rules}

        Analyze the video transcript and on-screen text against these rules.

        Return ONLY valid JSON:
        {{
        "compliance_results": [
        {{
            "category": "Claim Validation",
            "severity": "CRITICAL",
            "description": "Explanation of the violation..."
        }}
        ],
        "status": "FAIL",
        "final_report": "Summary of findings..."
        }}

        If there are no violations, use:
        "status": "PASS"
        and
        "compliance_results": []
        """

        user_message = f"""
        VIDEO METADATA: {state.get("video_metadata", {})}
        TRANSCRIPT: {transcript}
        ON-SCREEN TEXT: {ocr_text}
        """

        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ])

        content = response.content

        if "```" in content:
            match = re.search(r"```(?:json)?(.*?)```", content, re.DOTALL)
            if match:
                content = match.group(1)

        result = json.loads(content.strip())

        return {
            "compliance_results": result.get("compliance_results", []),
            "final_status": result.get("status", "FAIL"),
            "final_report": result.get("final_report", "No report generated."),
        }

    except Exception as error:
        logger.exception("Compliance audit failed")
        return {
            "errors": [str(error)],
            "final_status": "FAIL",
            "final_report": "The compliance audit could not be completed.",
        }
