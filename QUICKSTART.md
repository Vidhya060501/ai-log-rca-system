# Quick Start Guide

Get the RCA Chatbot up and running in minutes!

## Prerequisites Check

- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed  
- ✅ Docker installed and running
- ✅ OpenAI API key (get one at https://platform.openai.com/api-keys)

## Option 1: Docker Compose (Recommended)

1. **Clone and navigate to project**
   ```bash
   cd rca-chatbot
   ```

2. **Set up environment variables**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Start everything**
   ```bash
   cd ..
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Option 2: Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
uvicorn main:app --reload
```

### Frontend (in a new terminal)

```bash
cd frontend
npm install
npm run dev
```

## First Steps

1. **Upload some logs** using the sidebar
   - Try uploading sample logs or paste log entries directly

2. **Ask a question** in the chat
   - "What errors are in the logs?"
   - "Analyze the connection issues"
   - "What's causing the performance problems?"

3. **Explore the API** at http://localhost:8000/docs

## Sample Logs to Test

```
2024-01-15 10:23:45 ERROR Database connection failed: timeout after 30s
2024-01-15 10:23:46 WARN Retrying connection attempt 1/3
2024-01-15 10:23:47 ERROR Memory usage exceeded 90% threshold
2024-01-15 10:23:48 INFO Application restarting due to memory pressure
2024-01-15 10:24:00 ERROR Failed to process request: connection pool exhausted
```

## Troubleshooting

**Backend won't start:**
- Check that OPENAI_API_KEY is set in `.env`
- Ensure port 8000 is not in use

**Frontend can't connect:**
- Verify backend is running on port 8000
- Check browser console for errors

**Vector store issues:**
- FAISS will create index automatically
- For pgvector, ensure PostgreSQL is running and connection string is correct

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [AWS deployment guide](README.md#aws-deployment) for production setup
- Customize prompts in `backend/services/llm_service.py`


