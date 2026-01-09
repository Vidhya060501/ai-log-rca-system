from services.llm_service import LLMService
from services.vector_store import VectorStoreService
from typing import List, Optional, AsyncIterator
import logging
import uuid
from datetime import datetime
import re

NO_EVIDENCE_MSG = (
    "No evidence found in the uploaded/indexed logs to answer this question. "
    "Please upload relevant logs or refine your query."
)

class LogAnalyzer:
    def __init__(self, llm_service: LLMService, vector_store: VectorStoreService):
        self.llm_service = llm_service
        self.vector_store = vector_store

    async def ingest_logs(self, logs: List[str], metadata: Optional[dict] = None) -> dict:
        """Ingest and index logs for analysis"""
        try:
            metadatas = []
            for i, _log in enumerate(logs):
                log_metadata = {
                    "timestamp": datetime.now().isoformat(),
                    "log_index": i,
                    "source": metadata.get("source", "unknown") if metadata else "unknown",
                    "type": metadata.get("type", "application") if metadata else "application",
                }
                if metadata:
                    log_metadata.update(metadata)
                metadatas.append(log_metadata)

            await self.vector_store.add_documents(logs, metadatas)
            return {"indexed_count": len(logs), "status": "success"}

        except Exception as e:
            logging.error(f"Error ingesting logs: {str(e)}")
            raise

    # --- helper: evidence keywords for common topics ---
    def _evidence_keywords_for_query(self, query: str) -> List[str]:
        q = query.lower()

        # Kubernetes eviction / node pressure
        if any(k in q for k in ["pod eviction", "pod evict", "eviction", "evicted", "kubernetes eviction"]):
            return [
                "evict", "eviction", "evicted",
                "memorypressure", "diskpressure", "pidpressure", "outofdisk",
                "node pressure", "taint", "toleration",
                "kubelet", "preempt", "oomkilled", "oom killed",
            ]

        # Kafka rebalance / coordinator issues
        if any(k in q for k in ["rebalance", "re-balance", "group coordinator", "kafka rebalance"]):
            return [
                "rebalance", "rebalancing", "revok", "assign", "coordinator",
                "join group", "sync group", "heartbeat", "commit failed",
                "member", "group", "generation", "offset",
            ]

        return []

    def _has_topic_evidence(self, logs: List[dict], keywords: List[str]) -> bool:
        if not keywords:
            return True  # no topic filter requested
        pattern = re.compile("|".join(re.escape(k) for k in keywords), re.IGNORECASE)
        return any(pattern.search((l.get("content") or "")) for l in logs)

    def _top_relevance(self, logs: List[dict]) -> float:
        return max((float(r.get("relevance_score", 0.0) or 0.0) for r in logs), default=0.0)

    def _format_sources(self, relevant_logs: List[dict]) -> List[dict]:
        sources = []
        for i, log_entry in enumerate(relevant_logs):
            content = log_entry.get("content") or ""
            content = content if isinstance(content, str) else str(content)

            sources.append({
                "index": i + 1,
                "content": (content[:200] + "...") if len(content) > 200 else content,
                "metadata": log_entry.get("metadata", {}) or {},
                # ✅ correct: use relevance_score
                "relevance_score": float(log_entry.get("relevance_score", 0.0) or 0.0),
                # optional debug visibility
                "distance_score": float(log_entry.get("score", 0.0) or 0.0),
            })
        return sources

    async def analyze_query(self, query: str, session_id: Optional[str] = None) -> dict:
        """Analyze a query using RAG (Retrieval Augmented Generation)"""
        if not session_id:
            session_id = str(uuid.uuid4())

        try:
            relevant_logs = await self.vector_store.similarity_search_with_relevance(
                query=query,
                k=5,
                score_threshold=0.6
            )

            # Guardrail 1: nothing retrieved
            if not relevant_logs:
                return {"response": NO_EVIDENCE_MSG, "session_id": session_id, "sources": []}

            # ✅ Guardrail 2: retrieval is weak/unrelated (prevents wrong-topic answers)
            top_rel = self._top_relevance(relevant_logs)
            if top_rel < 0.65:
                return {"response": NO_EVIDENCE_MSG, "session_id": session_id, "sources": []}

            # Guardrail 3: wrong-topic evidence (negative-case correctness)
            keywords = self._evidence_keywords_for_query(query)
            if keywords and not self._has_topic_evidence(relevant_logs, keywords):
                return {
                    "response": (
                        "I did not find evidence in the retrieved logs for this specific issue. "
                        f"For your query, I expected log signals like: {', '.join(keywords[:8])}...\n\n"
                        "The closest matches I retrieved appear to be about a different issue. "
                        "Upload relevant logs or refine the query."
                    ),
                    "session_id": session_id,
                    "sources": self._format_sources(relevant_logs),
                }

            # Build context + sources
            context = "Relevant log entries:\n\n"
            for i, log_entry in enumerate(relevant_logs):
                content = log_entry.get("content") or ""
                content = content if isinstance(content, str) else str(content)
                context += f"Log Entry {i+1}:\n{content}\n"
                context += f"Metadata: {log_entry.get('metadata', {})}\n\n"

            sources = self._format_sources(relevant_logs)

            response_text = await self.llm_service.generate_response(
                query=query,
                context=context,
                session_id=session_id
            )

            return {"response": response_text, "session_id": session_id, "sources": sources}

        except Exception as e:
            logging.error(f"Error analyzing query: {str(e)}")
            return {"response": f"Error analyzing query: {str(e)}", "session_id": session_id, "sources": []}

    async def analyze_query_stream(self, query: str, session_id: Optional[str] = None) -> AsyncIterator[str]:
        """Streaming version of query analysis"""
        if not session_id:
            session_id = str(uuid.uuid4())

        try:
            relevant_logs = await self.vector_store.similarity_search_with_relevance(
                query=query,
                k=5,
                score_threshold=0.6
            )

            if not relevant_logs:
                yield NO_EVIDENCE_MSG
                return

            # ✅ same relevance guardrail for streaming
            top_rel = self._top_relevance(relevant_logs)
            if top_rel < 0.65:
                yield NO_EVIDENCE_MSG
                return

            keywords = self._evidence_keywords_for_query(query)
            if keywords and not self._has_topic_evidence(relevant_logs, keywords):
                yield (
                    "I did not find evidence in the retrieved logs for this specific issue. "
                    f"For your query, I expected signals like: {', '.join(keywords[:8])}...\n"
                    "Upload relevant logs or refine the query."
                )
                return

            context = "Relevant log entries:\n\n"
            for i, log_entry in enumerate(relevant_logs):
                content = log_entry.get("content") or ""
                content = content if isinstance(content, str) else str(content)
                context += f"Log Entry {i+1}:\n{content}\n\n"

            async for chunk in self.llm_service.generate_response_stream(
                query=query,
                context=context,
                session_id=session_id
            ):
                yield chunk

        except Exception as e:
            logging.error(f"Error in streaming analysis: {str(e)}")
            yield f"Error: {str(e)}"