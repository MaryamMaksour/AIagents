
from langchain_ollama import OllamaEmbeddings
from main.config import OLLAMA_BASE_URL, EMBED_MODEL

# A single shared embedder
embedder = OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_BASE_URL)

def embed_query(text: str):
    return embedder.embed_query(text)
