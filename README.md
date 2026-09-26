TuongGPT - Agentic AI Chatbot Platform

TuongGPT is a production-ready, full-stack Agentic AI Chatbot application powered by FastAPI, LangGraph, and the next-generation Google Gemini models. The platform seamlessly integrates dynamic tool calling (ReAct pattern), conversational retrieval-augmented generation (RAG with ChromaDB), real-time web grounding (Tavily Search API), long-term context memory, and a real-time streaming user interface using Server-Sent Events (SSE).

🌟 Key Features

Agentic ReAct Architecture (LangGraph): Autonomous decision-making pipeline that evaluates user input, executes intermediate tools (web search, document retrieval, math calculations, and persistent memory), and synthesizes grounded answers.

Multi-Model Support: Effortlessly switch between Google Gemini models dynamically from the frontend:

gemini-3.5-flash-lite: Ultra-low latency, optimized for fast conversational turnarounds.

gemini-3.6-flash: High-performance balance between computational speed and reasoning.

gemini-3.8-flash: Advanced multimodal reasoning, complex problem solving, and tool orchestration.

Thread-Scoped RAG Engine: Upload and index documents (.pdf, .txt, .docx) dynamically per session thread (thread_id) using ChromaDB vector embeddings.

Session & Memory Management: SQLite-backed conversational checkpoints and message history, featuring persistent session tracking, title updates, and safe conversation deletion.

Smoothed Real-Time Streaming (SSE): Stream responses token-by-token directly to the client with pacing control to avoid connection drops, buffer overflow, and JSON tool payload leakage.

Voice Dictation (Speech-to-Text): Integrated Web Speech API for seamless real-time speech recognition (Vietnamese and English).

Automated CI/CD Pipeline: Fully configured GitHub Actions workflow that executes syntax validation (flake8) and triggers zero-downtime deployments via Render Deploy Hooks.

🛠️ Technology Stack

Backend Framework: Python 3.11, FastAPI, Uvicorn, SQLAlchemy, SQLite

AI & Agent Orchestration: LangChain, LangGraph, Google GenAI SDK, Tavily Search API

Vector Store & Embeddings: ChromaDB

Frontend: Vanilla JavaScript, Modern CSS3 (Dark Theme), Server-Sent Events (SSE), Web Speech API

DevOps & Infrastructure: GitHub Actions, Render Web Services & Persistent Disks

📂 Project Directory Structure

TuongGPT/
├── .github/
│   └── workflows/
│       └── deploy.yml            # GitHub Actions CI/CD workflow
├── data/                         # Persistent storage (SQLite databases & checkpoints)
├── templates/
│   └── index.html                # Single-page ChatGPT-like web interface
├── uploads/                      # Temporary storage for RAG document processing
├── agent.py                      # LangGraph StateGraph, ReAct agent logic & LLM instances
├── database.py                   # SQLAlchemy models, SQLite schema & session CRUD
├── main.py                       # FastAPI entry point, REST endpoints & SSE generator
├── rag.py                        # Document ingestion, text chunking & ChromaDB handler
├── tools.py                      # Custom Agent tools (Web Search, Calculator, Memory, RAG)
├── render.yaml                   # Infrastructure-as-Code configuration for Render
├── requirements.txt              # Production dependencies
└── README.md                     # Project documentation


🚀 Local Installation & Setup

1. Prerequisites

Python: Version >= 3.10

Google Gemini API Key: Obtainable from Google AI Studio

Tavily API Key: Obtainable from Tavily AI (for real-time web search)

2. Clone and Setup Environment

Clone the repository:

git clone https://github.com/<tuong-38>/TuongGPT.git
cd TuongGPT

# on window
Create and activate a virtual environment:
conda create -n tuonggpt python-3.11 -y
conda activate tuonggpt



Install dependencies:

pip install --upgrade pip
pip install -r requirements.txt


3. Environment Variables

Create a .env file in the root directory:

GOOGLE_API_KEY="..."
GEMINI_MODEL="gemini-3.8-flash"
TAVILY_API_KEY="..."

# LangSmith Observability (Optional)
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="your_langsmith_api_key_here"
LANGSMITH_PROJECT="tuonggpt-production"


4. Run the Development Server

Start the application with Uvicorn:

uvicorn main:app --host 127.0.0.1 --port 8000 --reload


Open your browser and navigate to: http://127.0.0.1:8000

🌐 Cloud Deployment (Render with CI/CD)

1. Configure the Render Web Service

Sign in to Render Dashboard and connect your GitHub repository.

Configure the deployment settings:

Runtime: Python 3

Build Command: pip install -r requirements.txt

Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT

Auto-Deploy: Select No (Deployment will be triggered by GitHub Actions).

Under Environment Variables, provide:

GOOGLE_API_KEY

TAVILY_API_KEY

GEMINI_MODEL

Attach a Persistent Disk mounted at /opt/render/project/src/data (1 GB) to preserve SQLite records and vector stores across deployments.

2. Configure GitHub Actions Deploy Hook

In Render, navigate to Settings -> Deploy Hook -> click Create Deploy Hook and copy the generated URL.

In your GitHub repository, navigate to Settings -> Secrets and variables -> Actions -> New repository secret.

Create the secret:

Name: RENDER_DEPLOY_HOOK_URL

Value: Paste the Deploy Hook URL copied from Render.

Push your changes to the main branch. GitHub Actions will automatically validate the codebase and trigger the deployment hook upon success.