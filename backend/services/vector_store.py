import os
import logging
from typing import List, Optional

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# PGVector is optional
try:
    from langchain_community.vectorstores import PGVector  # preferred modern import
except Exception:
    PGVector = None

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document


class VectorStoreService:
    def __init__(self):
        self.embedding_model = None
        self.vector_store = None

        self.use_pgvector = os.getenv("USE_PGVECTOR", "false").lower() == "true"

        # In docker-compose, backend should call ollama service name (ollama:11434)
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.embed_model_name = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

        # ✅ IMPORTANT: initialize the splitter (you were missing this)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            separators=["\n\n", "\n", " ", ""],
        )

        self._initialize_embeddings()

    def _initialize_embeddings(self):
        """Initialize embedding model (Ollama)."""
        try:
            self.embedding_model = OllamaEmbeddings(
                base_url=self.ollama_base_url,
                model=self.embed_model_name,
            )
            logging.info("Ollama embeddings initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing Ollama embeddings: {str(e)}")
            self.embedding_model = None

    async def initialize(self):
        """Initialize vector store."""
        if not self.embedding_model:
            logging.warning("Cannot initialize vector store without embeddings")
            return

        try:
            if self.use_pgvector:
                if PGVector is None:
                    logging.warning("PGVector not installed/available. Falling back to FAISS.")
                    self.use_pgvector = False
                else:
                    connection_string = os.getenv("POSTGRES_CONNECTION_STRING")
                    if not connection_string:
                        logging.warning("POSTGRES_CONNECTION_STRING not set. Falling back to FAISS.")
                        self.use_pgvector = False
                    else:
                        self.vector_store = PGVector.from_existing_index(
                            embedding=self.embedding_model,
                            connection_string=connection_string,
                            collection_name="log_embeddings",
                        )
                        logging.info("PGVector initialized")

            if not self.use_pgvector:
                persist_directory = os.getenv("FAISS_PERSIST_DIR", "./faiss_index")
                os.makedirs(persist_directory, exist_ok=True)

                try:
                    # Many setups require allow_dangerous_deserialization=True for local FAISS load
                    self.vector_store = FAISS.load_local(
                        persist_directory,
                        self.embedding_model,
                        allow_dangerous_deserialization=True,
                    )
                    logging.info("Loaded existing FAISS index")
                except Exception as e:
                    logging.warning(f"FAISS load failed, creating a new index: {e}")
                    self.vector_store = FAISS.from_texts(
                        ["Initial document"],
                        self.embedding_model,
                    )
                    self.vector_store.save_local(persist_directory)
                    logging.info("Created new FAISS index")

        except Exception as e:
            logging.error(f"Error initializing vector store: {str(e)}")
            self.vector_store = None

    def is_available(self) -> bool:
        """Check if vector store is available."""
        return self.vector_store is not None and self.embedding_model is not None

    async def add_documents(self, texts: List[str], metadatas: Optional[List[dict]] = None):
        """Add documents to vector store."""
        if not self.vector_store or not self.embedding_model:
            raise ValueError("Vector store not initialized")

        documents: List[Document] = []

        for i, text in enumerate(texts):
            if not isinstance(text, str):
                text = str(text)

            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}

            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            for chunk in chunks:
                documents.append(Document(page_content=chunk, metadata=metadata))

        # Add to vector store
        if self.use_pgvector:
            await self.vector_store.aadd_documents(documents)
        else:
            self.vector_store.add_documents(documents)

            # Save FAISS index
            persist_directory = os.getenv("FAISS_PERSIST_DIR", "./faiss_index")
            self.vector_store.save_local(persist_directory)

        logging.info(f"Added {len(documents)} document chunks to vector store")

    async def similarity_search(self, query: str, k: int = 5) -> List[dict]:
        """Perform similarity search."""
        if not self.vector_store:
            return []

        try:
            if self.use_pgvector:
                docs = await self.vector_store.asimilarity_search_with_score(query, k=k)
            else:
                docs = self.vector_store.similarity_search_with_score(query, k=k)

            results = []
            for doc, score in docs:
                distance = float(score)
                # For FAISS, `score` is typically a distance (lower = more similar). Convert to a 0..1 relevance.
                relevance = 1.0 / (1.0 + distance)
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": distance,
                    "relevance_score": relevance,
                })

            return results
        except Exception as e:
            logging.error(f"Error in similarity search: {str(e)}")
            return []

    async def similarity_search_with_relevance(
        self, query: str, k: int = 5, score_threshold: float = 0.7
    ) -> List[dict]:
        """Similarity search with relevance threshold."""
        # Pull a larger candidate set, then filter using relevance_score when possible.
        results = await self.similarity_search(query, k=max(k * 4, 10))
        if not results:
            return []

        # Prefer relevance_score (0..1 where higher is better). If none pass threshold, fall back to top-k by distance.
        filtered = [r for r in results if r.get("relevance_score", 0.0) >= score_threshold]
        if not filtered:
            # Fallback: return the closest items (lowest distance)
            results_sorted = sorted(results, key=lambda x: x.get("score", float("inf")))
            return results_sorted[:k]

        # Order filtered by highest relevance
        filtered_sorted = sorted(filtered, key=lambda x: x.get("relevance_score", 0.0), reverse=True)
        return filtered_sorted[:k]