from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, AsyncIterator
import os
from dotenv import load_dotenv
import logging

from services.llm_service import LLMService
from services.vector_store import VectorStoreService
from services.log_analyzer import LogAnalyzer

load_dotenv()

app = FastAPI(title="RCA Chatbot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
llm_service = LLMService()
vector_store = VectorStoreService()
log_analyzer = LogAnalyzer(llm_service, vector_store)

# Request/Response models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class LogUpload(BaseModel):
    logs: List[str]
    metadata: Optional[dict] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: Optional[List[dict]] = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await vector_store.initialize()
    logging.info("RCA Chatbot API started")

@app.get("/")
async def root():
    return {"message": "RCA Chatbot API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": {
        "llm": llm_service.is_available(),
        "vector_store": vector_store.is_available()
    }}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Main chat endpoint for RCA queries"""
    try:
        response = await log_analyzer.analyze_query(
            query=message.message,
            session_id=message.session_id
        )
        return response
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/stream")
async def chat_stream(message: ChatMessage):
    """Streaming chat endpoint for real-time responses"""
    async def generate() -> AsyncIterator[str]:
        try:
            async for chunk in log_analyzer.analyze_query_stream(
                query=message.message,
                session_id=message.session_id
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logging.error(f"Error in streaming: {str(e)}")
            yield f"data: {str(e)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/api/logs/upload")
async def upload_logs(log_upload: LogUpload):
    """Upload logs for analysis and indexing"""
    try:
        result = await log_analyzer.ingest_logs(
            logs=log_upload.logs,
            metadata=log_upload.metadata
        )
        return {"status": "success", "indexed_count": result["indexed_count"]}
    except Exception as e:
        logging.error(f"Error uploading logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs/search")
async def search_logs(query: str, limit: int = 10):
    """Search logs using semantic search"""
    try:
        results = await vector_store.similarity_search(query, k=limit)
        return {"results": results}
    except Exception as e:
        logging.error(f"Error searching logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


