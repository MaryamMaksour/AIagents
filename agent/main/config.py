
import os

# --- Ollama ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://192.168.43.220:11435")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.0"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "10000"))
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "10m")
OLLAMA_MAX_WINDOW_TOKENS = os.getenv("OLLAMA_MAX_WINDOW_TOKENS", "32000")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-large")

# --- PostgreSQL / pgvector ---
PG_DBNAME = os.getenv("PG_DBNAME", "Evolution")
PG_USER = os.getenv("PG_USER", "ev")
PG_PASSWORD = os.getenv("PG_PASSWORD", "Temp@123")
PG_HOST = os.getenv("PG_HOST", "192.168.4.51")
PG_PORT = int(os.getenv("PG_PORT", "5432"))



# --- Retrieval distance operator: pgvector supports '<->'(L2), '<#>'(IP), '<=>'(cosine)
DIST_OP = os.getenv("DIST_OP", "<=>")  # choose based on how embeddings were normalized


