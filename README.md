# Azure Multi-Modal Video Compliance & Violation Detection System

An AI-based system that automatically checks advertisement videos for **compliance violations**.

It uses **Azure Video Indexer, Azure AI Search, Azure OpenAI, LangGraph, LangSmith, Azure Monitor, FastAPI, and HTML/CSS/JavaScript**.

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
PASS / FAIL Report
```

The workflow is managed using **LangGraph** and monitored using **LangSmith + Azure Monitor**.

## Main Features

- Takes a YouTube video URL
- Extracts speech and on-screen text
- Retrieves relevant compliance rules
- Uses RAG for compliance checking
- Uses Azure OpenAI for analysis
- Generates PASS/FAIL results
- Shows violations and severity
- Provides a final compliance report
- Uses LangSmith for tracing
- Uses Azure Monitor for monitoring
- Provides a simple web frontend

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

**Monitoring**
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
│       └── services/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── main.py
├── requirements.txt
├── .env
└── README.md
```

## RAG Flow

```text
Compliance PDFs
      ↓
Text Extraction
      ↓
Text Chunks
      ↓
Azure OpenAI Embeddings
      ↓
Azure AI Search
      ↓
Compliance Knowledge Base
```

During video analysis, the system searches this knowledge base and gives the relevant rules to Azure OpenAI.

## LangGraph Flow

```text
START
  ↓
Indexer
  ↓
Extract Video Information
  ↓
Auditor
  ↓
Retrieve Rules
  ↓
Azure OpenAI
  ↓
Compliance Result
  ↓
END
```

The project uses two main nodes: **Indexer** and **Auditor**.

## Example Result

```json
{
  "status": "FAIL",
  "compliance_results": [
    {
      "category": "Claim Validation",
      "severity": "CRITICAL",
      "description": "Compliance violation detected."
    }
  ],
  "final_report": "The advertisement requires compliance review."
}
```

## Run the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the server:

```bash
uvicorn backend.src.api.server:app --reload
```

Open:

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



## Environment Variables

The project uses `.env` for:

- Azure Video Indexer
- Azure OpenAI
- Azure AI Search
- LangSmith
- Azure Monitor

**Never upload `.env` or API keys to GitHub.**

## Resume Description

**Azure Multi-Modal Video Compliance & Violation Detection System**

Built a GenAI application using **Azure Video Indexer, Azure AI Search, Azure OpenAI, LangGraph, LangSmith, and RAG** to analyze advertisement videos, detect compliance violations, and generate structured PASS/FAIL reports. Added FastAPI, web frontend, and Azure Monitor for monitoring.

## Project Value

```text
Video Understanding
       +
RAG
       +
Azure OpenAI
       +
LangGraph
       +
LangSmith
       +
Azure Monitoring
       +
Web Application
```

This project demonstrates an end-to-end **enterprise GenAI + RAG + Agentic Workflow** application.