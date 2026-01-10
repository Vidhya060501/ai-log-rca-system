# 🔍 Intelligent RCA Chatbot (Log Analysis with RAG + Ollama)

A **full-stack Root Cause Analysis (RCA) chatbot** that performs **evidence-based log analysis using Retrieval-Augmented Generation (RAG)**.  
Built with **FastAPI, React, LangChain, FAISS, and Ollama**, this system guarantees that answers are generated **only from uploaded logs**, preventing hallucinations.

---

## ✨ Key Highlights

- ✅ **True RAG (Retrieval-Augmented Generation)**
- ✅ **Local LLM via Ollama (No OpenAI / No paid APIs)**
- ✅ **Semantic log search with FAISS**
- ✅ **Strict evidence-based answers**
- ✅ **Negative-case correctness (refuses wrong answers)**
- ✅ **Streaming chat responses**
- ✅ **Fully Dockerized**

---

## 🧠 What Makes This Project Different?

Unlike typical AI chatbots, this system:

- Uses **retrieved log evidence only**
- Refuses to speculate if logs do not support the question
- Detects **wrong-topic queries** (e.g., Kafka logs ≠ Kubernetes issues)
- Shows **exact log sources** used in answers

This makes it suitable for:
- Production RCA workflows
- SRE / DevOps analysis
- Interview demonstrations
- AI safety / grounding examples

---

## 🏗️ High-Level Architecture

User (Browser)
|
v
React Frontend
|
v
FastAPI Backend
|
|– FAISS Vector Store (log embeddings)
|

---

## 🧩 Actual RAG Workflow (Implemented)
|– Ollama (Local LLM)

1.	User uploads logs
	2.	Logs are chunked
	3.	Each chunk → embedding (Ollama embeddings)
	4.	Stored in FAISS vector index

When a user asks a question:
5. Query → embedding
6. FAISS similarity search
7. Relevant log chunks retrieved
8. Context + question → LLM prompt
9. LLM answers ONLY from context
10. If no evidence → hard refusal

✔ This is **real RAG**, not prompt stuffing.

---

## 🚀 Features

### 🔹 Log Ingestion
- Upload `.log` or `.txt` files
- Paste logs manually
- Each line indexed independently

### 🔹 Semantic Search
- FAISS-based vector similarity search
- Relevance scoring and filtering

### 🔹 Hallucination Guardrails
- No retrieved logs → **No answer**
- Wrong-topic logs → **Explicit rejection**
- Mandatory evidence requirement

### 🔹 Chat Interface
- Streaming responses
- Markdown formatting
- Source attribution per response

---

## 🧰 Tech Stack

### Backend
- FastAPI
- LangChain
- FAISS
- Ollama (Mistral / LLaMA-family models)

### Frontend
- React (Vite)
- Axios
- React Markdown

### Infrastructure
- Docker
- Docker Compose

---

## 📋 Prerequisites

- Docker
- Docker Compose

❌ No OpenAI API key required  
❌ No paid APIs  
❌ No cloud dependency for local use  

---

## 🛠️ Local Setup (Recommended)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/rca-chatbot.git
cd rca-chatbot

2️⃣ Start the Application

docker compose up --build

This launches:
	•	Ollama (LLM)
	•	FastAPI backend
	•	React frontend

⸻

3️⃣ Access the Application
	•	Frontend: http://localhost:3001
	•	Backend API: http://localhost:8000
	•	Swagger Docs: http://localhost:8000/docs

⸻

🧪 How to Use
	1.	Upload logs using the sidebar
	2.	Ask questions like:
	•	Any Kafka rebalance errors?
	•	Why did offset commits fail?
	•	Are there Kubernetes pod eviction errors?
	3.	The system:
	•	Answers only if evidence exists
	•	Refuses if logs don’t support the question

⸻

🔐 Hallucination Prevention (Critical Design)

The system will not:
	•	Guess missing data
	•	Invent root causes
	•	Cross-apply unrelated logs

If evidence is missing, the response is:

No evidence found in the uploaded/indexed logs to answer this question. Please upload relevant logs or refine your query.

This is enforced at:
	•	Vector retrieval layer
	•	Application logic layer
	•	LLM prompt level

⸻

📖 API Endpoints

| Method | Endpoint              | Description                 |
|--------|-----------------------|-----------------------------|
| POST   | /api/logs/upload      | Upload and index logs       |
| POST   | /api/chat             | Ask a chat question         |
| POST   | /api/chat/stream      | Streaming chat response     |
| GET    | /api/logs/search      | Semantic log search         |
| GET    | /health               | Health check                |

🐳 Docker Services

| Service Name | Container Name | Port Mapping        | Description                                      |
|-------------|----------------|---------------------|--------------------------------------------------|
| frontend    | rca-frontend   | 3001 → 80           | React UI served via Nginx                        |
| backend     | rca-backend    | 8000 → 8000         | FastAPI backend for RCA & RAG logic              |
| ollama      | rca-ollama     | 11434 → 11434       | Local LLM & embedding inference (Ollama)         |
| postgres*   | rca-postgres   | 5432 → 5432         | Optional pgvector store for embeddings           |

🔒 Security Notes
	•	No secrets committed
	•	.env files ignored via .gitignore
	•	Local-first architecture
	•	Ready for cloud secrets managers if deployed

⸻

📦 Deployment Status
	•	✅ Local Docker deployment
	•	✅ GitHub repository
	•	🔜 AWS ECS deployment (planned)

⸻

📜 License

MIT License

⸻

🤝 Contributing

Pull requests are welcome.

⸻


