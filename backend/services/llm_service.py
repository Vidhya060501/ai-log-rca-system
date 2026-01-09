from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from typing import Optional, AsyncIterator
import os
import logging

class LLMService:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        self.model_name = os.getenv("OLLAMA_MODEL", os.getenv("LLM_MODEL", "mistral"))
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        if self.provider != "ollama":
            logging.warning("LLM_PROVIDER is not 'ollama'. LLM will be disabled in free mode.")
            self.llm = None
        else:
            self.llm = ChatOllama(
                model=self.model_name,
                base_url=self.ollama_base_url,
                temperature=self.temperature,
            )

        self.memories = {}

        self.rca_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """You are an expert Root Cause Analysis (RCA) assistant specialized in log analysis and system diagnostics.

Your role is to:
1. Analyze log entries and identify patterns, errors, and anomalies
2. Provide clear, actionable root cause analysis
3. Suggest remediation steps
4. Explain technical concepts in a clear manner

Format responses with:
- Summary of findings
- Root cause
- Evidence
- Recommended actions"""
            ),
            HumanMessagePromptTemplate.from_template("{query}")
        ])

    def is_available(self) -> bool:
        return self.llm is not None

    def get_memory(self, session_id: str):
        if session_id not in self.memories:
            self.memories[session_id] = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
            )
        return self.memories[session_id]

    async def generate_response(self, query: str, context: Optional[str] = None, session_id: Optional[str] = None) -> str:
        if not self.llm:
            return "LLM service is not configured (ollama)."

        if context:
            query = f"Context from logs:\n{context}\n\nUser question: {query}"

        memory = self.get_memory(session_id) if session_id else None

        try:
            chain = LLMChain(
                llm=self.llm,
                prompt=self.rca_prompt,
                memory=memory,
                verbose=True
            )
            return await chain.arun(query=query)
        except Exception as e:
            logging.error(f"Error generating LLM response: {str(e)}")
            return f"Error generating response: {str(e)}"

    async def generate_response_stream(self, query: str, context: Optional[str] = None, session_id: Optional[str] = None) -> AsyncIterator[str]:
        if not self.llm:
            yield "LLM service is not configured (ollama)."
            return

        if context:
            query = f"Context from logs:\n{context}\n\nUser question: {query}"

        try:
            messages = self.rca_prompt.format_messages(query=query)
            async for chunk in self.llm.astream(messages):
                yield getattr(chunk, "content", str(chunk))
        except Exception as e:
            logging.error(f"Error in streaming response: {str(e)}")
            yield f"Error: {str(e)}"
    async def generate_response_stream(self, query: str, context: Optional[str] = None, session_id: Optional[str] = None) -> AsyncIterator[str]:
        """Generate streaming LLM response"""
        if not self.llm:
            yield "LLM service is not configured. Please set OPENAI_API_KEY environment variable."
            return
        
        if context:
            query = f"Context from logs:\n{context}\n\nUser question: {query}"
        
        try:
            messages = self.rca_prompt.format_messages(query=query)
            
            async for chunk in self.llm.astream(messages):
                if hasattr(chunk, 'content'):
                    yield chunk.content
                elif isinstance(chunk, str):
                    yield chunk
                else:
                    yield str(chunk)
        except Exception as e:
            logging.error(f"Error in streaming response: {str(e)}")
            yield f"Error: {str(e)}"

