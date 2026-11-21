# CyberSentinel-AI

An AI-powered cybersecurity threat investigation system using machine learning, semantic retrieval, LangGraph, and a locally hosted Llama 3.2 model.

## Features
- LANL authentication log processing
- Behavioral anomaly detection using machine learning
- Security alert generation and investigation
- Semantic cybersecurity knowledge retrieval
- LangGraph investigation workflow
- LLM-generated, evidence-grounded security assessments
- FastAPI endpoints for alerts and investigations

## Technology Stack
Python, FastAPI, Pandas, NumPy, Scikit-learn, Sentence Transformers, LangGraph, Ollama, Llama 3.2

## Run Locally

1. Create and activate a Python virtual environment.
2. Install the project dependencies.
3. Install Ollama and download `llama3.2:3b`.
4. Start the API:

   python -m uvicorn api.main:app --reload

5. Open http://127.0.0.1:8000/docs

## Data
The project uses LANL cybersecurity authentication data.
Large datasets and generated files are excluded from GitHub.

## Note
AI assessments are investigative recommendations, not confirmation of malicious activity.
