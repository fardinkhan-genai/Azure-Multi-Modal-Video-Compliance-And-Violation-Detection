# Azure Multi-Modal Video Compliance & Violation Detection System

An end-to-end Generative AI application that analyzes advertisement videos for potential compliance violations by combining **Azure Video Indexer, Azure AI Search, Azure OpenAI, LangGraph, LangSmith, Azure Monitor, FastAPI, and a lightweight HTML/CSS/JavaScript frontend**.

The system extracts information from a video, retrieves relevant compliance rules from a vector knowledge base, and uses an Azure OpenAI model to produce a structured compliance decision and report.

---

## 1. Project Overview

Organizations often review advertisement and promotional videos manually to check whether claims, on-screen text, and spoken content follow internal branding rules, advertising guidelines, and regulatory policies.

This project automates that workflow.

### What the system does

1. Accepts a YouTube video URL from the web interface.
2. Downloads the video using `yt-dlp`.
3. Uploads the video to Azure Video Indexer.
4. Uses Azure Video Indexer to extract:
   - Speech/transcript
   - OCR / on-screen text
   - Basic video metadata
5. Uses Azure AI Search as the compliance knowledge base.
6. Retrieves the most relevant compliance rules using vector similarity search.
7. Sends the video information and retrieved rules to Azure OpenAI.
8. Produces:
   - PASS / FAIL status
   - Compliance violations
   - Severity
   - Violation category
   - Final audit report
9. Orchestrates the processing using LangGraph.
10. Traces the workflow using LangSmith.
11. Sends application telemetry to Azure Monitor / Application Insights.
12. Displays the final result in the frontend.

---

## 2. Architecture

```text
                    ┌──────────────────────────────┐
                    │       Web Frontend           │
                    │     HTML + CSS + JavaScript  │
                    └──────────────┬───────────────┘
                                   │
                              POST /audit
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │          FastAPI             │
                    │       REST API Layer         │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │          LangGraph            │
                    │      Workflow Orchestrator    │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │       Indexer Node            │
                    │                               │
                    │  YouTube → yt-dlp             │
                    │          ↓                    │
                    │  Azure Video Indexer         │
                    │          ↓                    │
                    │  Transcript + OCR + Metadata  │
                    └──────────────┬────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │        Auditor Node           │
                    │                               │
                    │   Video information           │
                    │          +                    │
                    │   Retrieved compliance rules  │
                    └──────────────┬───────────────┘
                                   │
                         ┌─────────┴─────────┐
                         │                   │
                         ▼                   ▼
                ┌─────────────────┐  ┌─────────────────┐
                │ Azure AI Search │  │  Azure OpenAI   │
                │ Compliance KB   │  │ Compliance LLM  │
                └────────┬────────┘  └────────┬────────┘
                         │                    │
                         └─────────┬──────────┘
                                   ▼
                    ┌──────────────────────────────┐
                    │     Structured Audit Result   │
                    │                               │
                    │  PASS / FAIL                 │
                    │  Violations                  │
                    │  Severity                    │
                    │  Category                    │
                    │  Final Report                │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │          Frontend             │
                    │       Display Result          │
                    └──────────────────────────────┘


Observability:

        FastAPI / LangGraph / LLM Workflow
                  │
          ┌───────┴────────┐
          ▼                ▼
     LangSmith        Azure Monitor
     Tracing           / Application
                       Insights
```

---

## 3. RAG Architecture

The compliance knowledge base is created from PDF documents stored in:

```text
backend/data/
```

Examples include advertising and influencer compliance guidelines.

The indexing script:

```text
backend/scripts/index_documents.py
```

performs:

```text
PDF Documents
      ↓
PyPDFLoader
      ↓
Text Extraction
      ↓
Recursive Character Text Splitter
      ↓
Azure OpenAI Embeddings
      ↓
Azure AI Search
      ↓
Vector Knowledge Base
```

During an audit:

```text
Video Transcript + OCR
          ↓
      Search Query
          ↓
Azure AI Search
          ↓
Top Relevant Compliance Rules
          ↓
Azure OpenAI
```

This is a Retrieval-Augmented Generation (RAG) workflow because the LLM receives retrieved compliance knowledge instead of relying only on its pretrained knowledge.

---

## 4. LangGraph Workflow

The application uses a simple two-node LangGraph workflow:

```text
START
  │
  ▼
┌───────────────┐
│    indexer    │
│               │
│ Download      │
│ Video Indexer │
│ Transcript    │
│ OCR           │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│    auditor    │
│               │
│ Retrieve      │
│ Rules         │
│      ↓        │
│ Azure OpenAI  │
│      ↓        │
│ Compliance    │
│ Decision      │
└───────┬───────┘
        │
        ▼
       END
```

### Node 1 — Indexer

Implemented in:

```text
backend/src/graph/nodes.py
```

Responsibilities:

- Validate the YouTube URL.
- Download the video.
- Upload it to Azure Video Indexer.
- Wait for indexing to finish.
- Extract transcript.
- Extract OCR text.
- Return video metadata.

### Node 2 — Auditor

Responsibilities:

- Create the Azure OpenAI chat model.
- Create the Azure OpenAI embedding model.
- Connect to Azure AI Search.
- Retrieve relevant compliance rules.
- Build the audit prompt.
- Analyze transcript and OCR content.
- Parse the model's JSON response.
- Return structured compliance results.

---

## 5. Compliance Result

The application produces a structured result similar to:

```json
{
  "status": "FAIL",
  "compliance_results": [
    {
      "category": "Claim Validation",
      "severity": "CRITICAL",
      "description": "The advertisement contains a claim that is not supported by the retrieved compliance rules."
    }
  ],
  "final_report": "The advertisement requires compliance review before publication."
}
```

If no violations are detected:

```json
{
  "status": "PASS",
  "compliance_results": [],
  "final_report": "No compliance violations were identified."
}
```

---

## 6. Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- Uvicorn

### Generative AI

- Azure OpenAI
- LangChain
- LangGraph
- RAG
- Azure OpenAI Embeddings

### Azure Services

- Azure Video Indexer
- Azure AI Search
- Azure Monitor
- Application Insights
- Azure Identity

### Observability

- LangSmith
- Azure Monitor / Application Insights
- Python logging

### Video Processing

- yt-dlp
- Azure Video Indexer

### Frontend

- HTML5
- CSS3
- JavaScript

### Document Processing

- PyPDF
- RecursiveCharacterTextSplitter

---

## 7. Project Structure

```text
Azure Multi-Modal Video Compliance & Violation Detection/
│
├── backend/
│   ├── data/
│   │   ├── 1001a-influencer-guide-508_1.pdf
│   │   └── youtube-ad-specs.pdf
│   │
│   ├── scripts/
│   │   ├── index_documents.py
│   │   └── explanation.txt
│   │
│   └── src/
│       ├── api/
│       │   ├── server.py
│       │   └── telemetry.py
│       │   
│       │
│       ├── graph/
│       │   ├── state.py
│       │   ├── nodes.py
│       │   └── workflow.py
│       │   
│       │
│       └── services/
│           └── video_indexer.py
│
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── main.py
├── requirements.txt
├── pyproject.toml
├── uv.lock
├── .env
├── .gitignore
├── README.md
└── WorkFlow.txt
```

---

## 8. Environment Variables

The application expects Azure and LangSmith configuration through `.env`.

Typical configuration includes:

```env
# Azure Video Indexer
AZURE_VI_ACCOUNT_ID=
AZURE_VI_LOCATION=
AZURE_SUBSCRIPTION_ID=
AZURE_RESOURCE_GROUP=
AZURE_VI_NAME=

# Azure OpenAI
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_VERSION=
AZURE_OPENAI_CHAT_DEPLOYMENT=
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=

# Azure AI Search
AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_API_KEY=
AZURE_SEARCH_INDEX_NAME=

# LangSmith
LANGCHAIN_TRACING_V2=
LANGCHAIN_ENDPOINT=
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=

# Azure Monitor
APPLICATIONINSIGHTS_CONNECTION_STRING=
```

Use the variable names expected by the application. Do not commit real API keys or connection strings to GitHub.

---

## 9. Installation

Create and activate a Python environment.

Then install the dependencies:

```bash
pip install -r requirements.txt
```

Or, if using `uv`:

```bash
uv sync
```

---

## 10. Prepare the Knowledge Base

Place compliance PDF documents inside:

```text
backend/data/
```

Then run:

```bash
python backend/scripts/index_documents.py
```

The script:

1. Reads the PDFs.
2. Extracts the text.
3. Splits the text into chunks.
4. Generates embeddings using Azure OpenAI.
5. Stores the chunks and vectors in Azure AI Search.

The Azure AI Search index must be configured before running the application.

---

## 11. Run the Application

Start FastAPI:

```bash
uvicorn backend.src.api.server:app --reload
```

Open:

```text
http://localhost:8000/
```

### Health Check

```text
http://localhost:8000/health
```

### API Documentation

```text
http://localhost:8000/docs
```

---

## 12. API

### POST `/audit`

Request:

```json
{
  "video_url": "https://youtu.be/example"
}
```

The API starts the complete LangGraph workflow and returns the audit result.

### GET `/health`

Returns the application health status.

---

## 13. Observability

### LangSmith

LangSmith is used to trace the LangGraph/LLM workflow.

The application records workflow information such as:

- Project
- Workflow name
- Session ID
- Video ID
- Tags
- Metadata
- LLM workflow execution

### Azure Monitor / Application Insights

Azure Monitor is configured through:

```text
backend/src/api/telemetry.py
```

It provides application-level telemetry for monitoring and diagnostics.

---

## 14. Error Handling

The workflow handles failures at the video-indexing and compliance-analysis stages.

Examples include:

- Invalid YouTube URL
- YouTube download failure
- Azure Video Indexer failure
- Video processing failure
- Azure AI Search failure
- Azure OpenAI failure
- Invalid LLM JSON response
- Missing transcript

The API returns an HTTP 500 response when the workflow fails at the API level.

---

## 15. Security Notes

Do not commit:

```text
.env
```

to a public GitHub repository.

Never expose:

- Azure API keys
- Azure Search keys
- LangSmith API keys
- Application Insights connection strings
- Access tokens

Use Azure Identity / managed identity where appropriate when deploying to Azure.

---

## 16. Current Scope

This implementation is designed as a focused proof-of-concept for video compliance auditing.

Current input:

```text
YouTube URL
```

Current extracted information:

```text
Transcript
OCR / On-screen Text
Video Metadata
```

Current compliance knowledge source:

```text
PDF → Azure AI Search
```

Current AI analysis:

```text
Azure OpenAI
```

Current orchestration:

```text
LangGraph
```

Current observability:

```text
LangSmith + Azure Monitor
```

---

## 17. Future Enhancements

Possible production improvements include:

- Direct video file upload
- Azure Blob Storage for raw videos
- Timestamp-level violation detection
- Frame/image analysis using a vision model
- Multi-modal image + transcript reasoning
- Human approval workflow
- Authentication and authorization
- Background job processing
- Queue-based video processing
- Persistent audit history
- Dashboard and analytics
- More advanced RAG / hybrid search
- Automated compliance report export
- Deployment to Azure Container Apps or Azure App Service

---

## 18. Project Value

This project demonstrates an end-to-end enterprise-style Generative AI workflow combining:

```text
Video Understanding
        +
RAG
        +
LLM Reasoning
        +
Agent/Workflow Orchestration
        +
Cloud AI Services
        +
Observability
        +
Web Application
```

It is particularly useful as a portfolio project because it shows how an LLM can be connected to enterprise data, cloud AI services, retrieval systems, workflow orchestration, and production-oriented monitoring rather than being used as a standalone chatbot.

---

## 19. Resume-Ready Description

**Azure Multi-Modal Video Compliance & Violation Detection System**  
Built an end-to-end GenAI application using Azure Video Indexer, Azure AI Search, Azure OpenAI, LangGraph, and LangSmith to automatically analyze advertisement videos, extract transcript/OCR data, retrieve relevant compliance policies using RAG, and generate structured PASS/FAIL compliance reports with violation severity and explanations. Implemented FastAPI APIs, a separate HTML/CSS/JavaScript frontend, and Azure Monitor observability.

---

## 20. Disclaimer

This project is an AI-assisted compliance screening system and should be treated as a decision-support tool. Final regulatory, legal, or publication decisions should be reviewed by an appropriate human compliance professional.
