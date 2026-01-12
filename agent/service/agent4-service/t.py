
import requests

payload = {"session_id": "user-123", "user_input": "Explain RAG briefly."}
r = requests.post("http://localhost:8001/chat", json=payload, timeout=3600)
r.raise_for_status()
print(r.json())
