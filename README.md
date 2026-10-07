# Azure Multi-Modal Video Compliance & Violation Detection System

An end-to-end **GenAI application** that analyzes advertisement videos and detects potential compliance violations using **Azure Video Indexer, Azure AI Search, Azure OpenAI, RAG, LangGraph, and Guardrails AI**.

## How It Works

```text
YouTube Video
     ↓
Azure Video Indexer
     ↓
Transcript + OCR + Metadata
     ↓
Azure AI Search
     ↓
Compliance Rules
     ↓
Azure OpenAI
     ↓
Guardrails AI
     ↓
PASS / FAIL / REQUIRES_REVIEW
```

The workflow is orchestrated using **LangGraph** and monitored using **LangSmith and Azure Monitor**.

## Key Features

- YouTube video processing
- Speech/transcript extraction
- OCR and on-screen text extraction
- RAG-based compliance rule retrieval
- Azure OpenAI compliance analysis
- Guardrails AI output validation
- Violation detection with severity
- Structured compliance reports
- LangGraph workflow orchestration
- LangSmith tracing
- Azure Monitor/Application Insights
- FastAPI backend
- HTML/CSS/JavaScript frontend

## Technology Stack

**Backend**
- Python
- FastAPI
- Pydantic

**GenAI**
- Azure OpenAI
- LangChain
- LangGraph
- RAG
- Guardrails AI
- Azure OpenAI Embeddings

**Azure**
- Azure Video Indexer
- Azure AI Search
- Azure Monitor
- Application Insights

**Frontend**
- HTML
- CSS
- JavaScript

**Observability**
- LangSmith
- Azure Monitor

## Project Structure

```text
project/
│
├── backend/
│   ├── data/
│   ├── scripts/
│   └── src/
│       ├── api/
│       ├── graph/
│       ├── guardrails/
│       └── services/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── main.py
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

## RAG Pipeline

Compliance documents are converted into embeddings and stored in **Azure AI Search**.

```text
Compliance Documents
        ↓
Text Extraction & Chunking
        ↓
Azure OpenAI Embeddings
        ↓
Azure AI Search
        ↓
Relevant Compliance Rules
        ↓
Azure OpenAI
```

During video analysis, the system retrieves relevant rules and provides them to the LLM for compliance evaluation.

## LangGraph Workflow

```text
START
  ↓
Indexer
  ↓
Extract Video Information
  ↓
Auditor
  ↓
Retrieve Compliance Rules
  ↓
Azure OpenAI
  ↓
Guardrails Validation
  ↓
Compliance Result
  ↓
END
```

### Main Nodes

**Indexer**
- Processes the video using Azure Video Indexer.
- Extracts transcript, OCR, and metadata.

**Auditor**
- Retrieves compliance rules using Azure AI Search.
- Performs RAG-based analysis with Azure OpenAI.
- Validates the generated response using Guardrails AI.

## Example Result

```json
{
  "status": "FAIL",
  "compliance_results": [
    {
      "category": "Claim Validation",
      "severity": "CRITICAL",
      "description": "The advertisement contains an unsupported claim."
    }
  ],
  "final_report": "The advertisement requires compliance review."
}
```

Possible statuses:

```text
PASS
FAIL
REQUIRES_REVIEW
```

## Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scriptsctivate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your `.env` file with the required Azure, LangSmith, and Application Insights credentials.

## Run the Project

Start the FastAPI server:

```bash
uvicorn backend.src.api.server:app --reload
```

Open the application:

```text
http://localhost:8000/
```

API documentation:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

## Monitoring

**LangSmith** is used for LLM and LangGraph tracing, while **Azure Monitor/Application Insights** is used for application monitoring, errors, and performance.


> **Security:** Never commit `.env`, API keys, or Azure credentials to GitHub. Use `.env.example` for configuration reference.
