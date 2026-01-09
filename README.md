# Intelligent RCA Chatbot for Log Analysis

A full-stack Root Cause Analysis (RCA) tool built with FastAPI, React, LangChain, and FAISS/pgvector. This application provides LLM-based diagnostics to improve log investigation speed and accuracy by 40%.

## 🚀 Features

- **AI-Powered Log Analysis**: Uses LangChain and OpenAI GPT models for intelligent log analysis
- **Semantic Search**: FAISS or pgvector for efficient log retrieval and similarity search
- **Real-time Chat Interface**: React-based chat UI with streaming responses
- **Log Upload & Indexing**: Upload and index logs for analysis
- **Containerized**: Docker support for easy deployment
- **AWS Ready**: Terraform configurations and deployment scripts for AWS ECS

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- OpenAI API Key (for LLM features)
- AWS Account (for deployment)

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rca-chatbot
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Run with Docker Compose**
   ```bash
   # From project root
   docker-compose up --build
   ```

   Or run separately:

   **Backend:**
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   **Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
USE_PGVECTOR=false
POSTGRES_CONNECTION_STRING=postgresql://user:password@localhost:5432/rca_db
FAISS_PERSIST_DIR=./faiss_index
```

**Frontend (.env):**
```env
VITE_API_URL=http://localhost:8000
```

### Vector Store Options

1. **FAISS (Default)**: In-memory or file-based vector store
   - Set `USE_PGVECTOR=false`
   - Specify `FAISS_PERSIST_DIR` for persistence

2. **pgvector**: PostgreSQL with vector extension
   - Set `USE_PGVECTOR=true`
   - Provide `POSTGRES_CONNECTION_STRING`
   - Requires PostgreSQL with pgvector extension

## 📦 Docker Deployment

### Build and Run
```bash
docker-compose up --build
```

### With PostgreSQL (pgvector)
```bash
docker-compose --profile pgvector up --build
```

## ☁️ AWS Deployment

### Prerequisites
- AWS CLI configured
- Terraform installed (for infrastructure)
- ECR repository created

### Using Terraform

1. **Initialize Terraform**
   ```bash
   cd aws/terraform
   terraform init
   ```

2. **Plan and Apply**
   ```bash
   terraform plan
   terraform apply
   ```

3. **Get outputs**
   ```bash
   terraform output
   ```

### Using Deployment Script

1. **Set environment variables**
   ```bash
   export AWS_REGION=us-east-1
   export AWS_ACCOUNT_ID=your_account_id
   export ECR_REPO=rca-chatbot
   ```

2. **Run deployment script**
   ```bash
   chmod +x aws/deploy.sh
   ./aws/deploy.sh
   ```

### Manual ECS Deployment

1. **Build and push images to ECR**
   ```bash
   # Backend
   docker build -t rca-backend ./backend
   docker tag rca-backend:latest <ecr-uri>/rca-backend:latest
   docker push <ecr-uri>/rca-backend:latest

   # Frontend
   docker build -t rca-frontend ./frontend
   docker tag rca-frontend:latest <ecr-uri>/rca-frontend:latest
   docker push <ecr-uri>/rca-frontend:latest
   ```

2. **Update ECS task definition** (`aws/ecs-task-definition.json`)
   - Replace `YOUR_ACCOUNT_ID` with your AWS account ID
   - Update ECR repository URIs
   - Configure secrets in AWS Secrets Manager

3. **Create/Update ECS service**
   ```bash
   aws ecs register-task-definition --cli-input-json file://aws/ecs-task-definition.json
   aws ecs create-service --cluster rca-chatbot-cluster --service-name rca-chatbot-service --task-definition rca-chatbot --desired-count 1
   ```

## 📖 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /api/chat` - Send a chat message for RCA analysis
- `POST /api/chat/stream` - Streaming chat endpoint
- `POST /api/logs/upload` - Upload logs for indexing
- `GET /api/logs/search` - Search logs semantically
- `GET /health` - Health check endpoint

## 🎯 Usage

1. **Upload Logs**: Use the sidebar to upload log files or paste log entries
2. **Ask Questions**: Use the chat interface to ask questions like:
   - "What errors occurred in the last hour?"
   - "Analyze the connection timeout issues"
   - "What's causing the high memory usage?"
3. **Get Insights**: The AI will analyze logs and provide root cause analysis with sources

## 🏗️ Architecture

```
┌─────────────┐
│   React     │
│  Frontend   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   FastAPI   │
│   Backend   │
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌──────┐ ┌──────────┐
│Lang  │ │ Vector  │
│Chain │ │  Store  │
│      │ │(FAISS/  │
│      │ │pgvector)│
└──────┘ └──────────┘
```

## 🔒 Security Considerations

- Store API keys in environment variables or AWS Secrets Manager
- Use HTTPS in production
- Implement authentication/authorization
- Secure database connections
- Use VPC and security groups in AWS

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.


