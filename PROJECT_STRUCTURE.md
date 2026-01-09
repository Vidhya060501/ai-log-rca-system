# Project Structure

```
rca-chatbot/
├── backend/                    # FastAPI backend application
│   ├── main.py                # FastAPI app entry point
│   ├── services/              # Core services
│   │   ├── __init__.py
│   │   ├── llm_service.py     # LangChain LLM integration
│   │   ├── vector_store.py    # FAISS/pgvector integration
│   │   └── log_analyzer.py    # Main RCA analysis logic
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile            # Backend container config
│   └── .env.example          # Environment variables template
│
├── frontend/                  # React frontend application
│   ├── src/
│   │   ├── App.jsx           # Main app component
│   │   ├── main.jsx          # React entry point
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx    # Chat UI component
│   │   │   ├── ChatInterface.css
│   │   │   ├── LogUpload.jsx        # Log upload component
│   │   │   └── LogUpload.css
│   │   └── index.css         # Global styles
│   ├── package.json          # Node dependencies
│   ├── vite.config.js        # Vite configuration
│   ├── Dockerfile           # Frontend container config
│   └── nginx.conf           # Nginx config for production
│
├── aws/                      # AWS deployment configurations
│   ├── ecs-task-definition.json  # ECS task definition
│   ├── deploy.sh            # Deployment script
│   └── terraform/           # Infrastructure as Code
│       └── main.tf          # Terraform configuration
│
├── docker-compose.yml        # Docker Compose configuration
├── .dockerignore            # Docker ignore patterns
├── .gitignore              # Git ignore patterns
├── Makefile                # Convenience commands
├── README.md               # Main documentation
├── QUICKSTART.md           # Quick start guide
└── PROJECT_STRUCTURE.md    # This file
```

## Key Components

### Backend (FastAPI)
- **main.py**: API endpoints for chat, log upload, and search
- **llm_service.py**: Manages LLM interactions using LangChain
- **vector_store.py**: Handles vector embeddings and similarity search
- **log_analyzer.py**: Orchestrates RAG (Retrieval Augmented Generation) workflow

### Frontend (React + Vite)
- **ChatInterface**: Real-time chat UI with streaming support
- **LogUpload**: File upload and text paste interface for logs
- Modern UI with gradient design and responsive layout

### Infrastructure
- **Docker**: Containerized deployment
- **AWS ECS**: Container orchestration
- **Terraform**: Infrastructure provisioning
- **PostgreSQL + pgvector**: Optional vector database

## Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **Frontend**: React 18, Vite
- **AI/ML**: LangChain, OpenAI GPT-4
- **Vector DB**: FAISS (default), pgvector (optional)
- **Containerization**: Docker, Docker Compose
- **Cloud**: AWS ECS, RDS, ALB
- **IaC**: Terraform


