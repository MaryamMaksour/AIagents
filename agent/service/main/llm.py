from langchain_ollama import ChatOllama
from main.config import (
    OLLAMA_MODEL, OLLAMA_BASE_URL, OLLAMA_TEMPERATURE,
    OLLAMA_NUM_PREDICT, OLLAMA_KEEP_ALIVE
)




_llm = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=OLLAMA_TEMPERATURE,
    num_predict=OLLAMA_NUM_PREDICT,
    keep_alive=OLLAMA_KEEP_ALIVE,
    timeout=3600,  # seconds
    stream=True,
)

def get_llm():
    return _llm


