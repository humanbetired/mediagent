import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
import os

# ── Config ──────────────────────────────────────────────
KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR", "./knowledge_base")
CHROMA_DB_PATH     = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
OLLAMA_BASE_URL    = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL          = os.getenv("LLM_MODEL", "llama3.2:1b")
EMBED_MODEL        = os.getenv("EMBED_MODEL", "nomic-embed-text")


# ── Init LLM + Embedding ────────────────────────────────
def init_settings():
    Settings.llm = Ollama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        request_timeout=120.0
    )
    Settings.embed_model = OllamaEmbedding(
        model_name=EMBED_MODEL,
        base_url=OLLAMA_BASE_URL
    )
    Settings.chunk_size = 512
    Settings.chunk_overlap = 50

# ── Build / Load Index ──────────────────────────────────
def get_rag_index():
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)

    chroma_client     = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    chroma_collection = chroma_client.get_or_create_collection("medical_knowledge")
    vector_store      = ChromaVectorStore(chroma_collection=chroma_collection)

    # Kalau collection sudah ada isinya, langsung load
    if chroma_collection.count() > 0:
        print(f"[RAG] Loading existing index — {chroma_collection.count()} chunks found")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            storage_context=storage_context
        )
    else:
        print("[RAG] Building new index from knowledge base...")
        documents = SimpleDirectoryReader(KNOWLEDGE_BASE_DIR).load_data()
        print(f"[RAG] Loaded {len(documents)} documents")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=True
        )
        print("[RAG] Index built and persisted to ChromaDB")

    return index

# ── Query Engine ────────────────────────────────────────
def get_query_engine(index, similarity_top_k=3):
    return index.as_query_engine(
        similarity_top_k=similarity_top_k,
        response_mode="compact"
    )

# ── Medical RAG Agent ───────────────────────────────────
class MedicalRAGAgent:
    def __init__(self):
        print("[MedicalRAGAgent] Initializing...")
        init_settings()
        self.index        = get_rag_index()
        self.query_engine = get_query_engine(self.index)
        print("[MedicalRAGAgent] Ready")

    def query(self, question: str) -> dict:
        print(f"\n[MedicalRAGAgent] Query: {question}")
        response = self.query_engine.query(question)

        sources = []
        if hasattr(response, "source_nodes"):
            for node in response.source_nodes:
                sources.append({
                    "file"  : node.metadata.get("file_name", "unknown"),
                    "score" : round(node.score, 4) if node.score else None,
                    "text"  : node.text[:200] + "..."
                })

        return {
            "question" : question,
            "answer"   : str(response),
            "sources"  : sources
        }