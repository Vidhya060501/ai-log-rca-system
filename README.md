AI Log Root Cause Analysis System

⚠️ This repository is an experimental project exploring AI-assisted root cause analysis for large-scale application logs using retrieval-augmented generation (RAG).

The system indexes logs into vector embeddings and retrieves relevant failure patterns to help engineers diagnose production incidents across distributed services.

Unlike typical AI chatbots, this system enforces evidence-based answers, meaning responses are generated strictly from retrieved log context rather than speculation.

⸻

Engineering Motivation

Debugging distributed systems often requires engineers to manually search through thousands of logs across multiple services. Important signals are frequently buried within repetitive log patterns, making root cause discovery slow and error-prone.

This project explores how vector search + retrieval-augmented generation (RAG) can accelerate incident diagnosis by retrieving relevant log evidence and summarizing it in context.

The goal is to experiment with building AI-assisted observability tools that help engineers navigate large volumes of operational logs more efficiently.

⸻

Key Capabilities
	•	Evidence-based root cause analysis using retrieved log context
	•	Semantic log search using FAISS vector embeddings
	•	Local LLM inference via Ollama (no external API dependencies)
	•	Hallucination prevention by enforcing context-only responses
	•	Streaming chat responses
	•	Fully containerized deployment with Docker

⸻

High-Level Architecture

User (Browser)
      │
      ▼
React Frontend
      │
      ▼
FastAPI Backend
      │
      ├── Log ingestion + chunking
      ├── Embedding generation
      │
      ▼
FAISS Vector Store
      │
      ▼
Context Retrieval
      │
      ▼
LLM (Ollama)
      │
      ▼
Root Cause Summary


⸻

Retrieval-Augmented Log Analysis Workflow

Log ingestion:
	1.	Logs are uploaded or pasted into the system
	2.	Logs are chunked into smaller segments
	3.	Each chunk is converted into vector embeddings
	4.	Embeddings are stored in a FAISS vector index

Query workflow:
	5.	User question is converted to an embedding
	6.	FAISS retrieves the most relevant log chunks
	7.	Retrieved logs are passed as context to the LLM
	8.	LLM generates a response strictly from retrieved evidence

If no relevant logs are retrieved, the system refuses to generate an answer.

⸻

Features

Log Ingestion
	•	Upload .log or .txt files
	•	Manual log paste support
	•	Independent indexing of log lines

Semantic Log Search
	•	Vector similarity search using FAISS
	•	Relevant log chunks retrieved based on query meaning

Hallucination Guardrails

The system prevents speculative answers:
	•	No retrieved logs → no response generated
	•	Irrelevant logs → explicit rejection
	•	Responses must reference actual log evidence

Interactive Chat Interface
	•	Streaming responses
	•	Markdown formatting
	•	Source attribution for retrieved log evidence

⸻

Technology Stack

Backend
	•	FastAPI
	•	LangChain
	•	FAISS
	•	Ollama (local LLM inference)

Frontend
	•	React (Vite)
	•	Axios
	•	React Markdown

Infrastructure
	•	Docker
	•	Docker Compose

⸻

Prerequisites
	•	Docker
	•	Docker Compose

No external API keys required.

The system runs entirely with local models via Ollama.

⸻

Local Setup

Clone the repository

git clone https://github.com/Vidhya060501/ai-log-rca-system.git
cd ai-log-rca-system

Start the application

docker compose up --build

This launches:
	•	React frontend
	•	FastAPI backend
	•	Ollama for local LLM inference

⸻

Access the Application

Frontend
http://localhost:3001

Backend API
http://localhost:8000

Swagger documentation
http://localhost:8000/docs

⸻

Example Usage
	1.	Upload log files
	2.	Ask diagnostic questions such as:

	•	Why did the Kafka consumer fail?
	•	Are there timeout errors in the payment service?
	•	Did any Kubernetes pods crash recently?

	3.	The system retrieves relevant logs and generates an evidence-based explanation.

If no evidence is found, the system explicitly states that the logs do not support the query.

⸻

API Endpoints

Method	Endpoint	Description
POST	/api/logs/upload	Upload and index logs
POST	/api/chat	Ask a question
POST	/api/chat/stream	Streaming chat response
GET	/api/logs/search	Semantic log search
GET	/health	Health check


⸻

Docker Services

Service	Port	Description
frontend	3001	React UI
backend	8000	FastAPI backend
ollama	11434	Local LLM + embeddings

Optional:

Service	Port	Description
postgres	5432	pgvector store (optional)


⸻

Security Notes
	•	No secrets committed to the repository
	•	.env files excluded via .gitignore
	•	Local-first architecture
	•	Can be integrated with cloud secret managers if deployed

⸻

Current Limitations
	•	Retrieval quality depends heavily on log chunking strategy
	•	Large log datasets may require improved indexing techniques
	•	Prompt structure for summarization is still being refined

This repository is actively evolving as I experiment with improving log retrieval pipelines and root cause summarization methods.

⸻

Deployment Status

Current
	•	Local Docker deployment
	•	GitHub repository

Planned
	•	Cloud deployment (AWS ECS)

⸻

License

MIT License

⸻

Contributing

Pull requests and experimentation ideas are welcome.
