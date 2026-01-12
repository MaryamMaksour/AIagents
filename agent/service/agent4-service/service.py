
# app/service.py
from typing import Dict, List, Optional
from threading import RLock
import time

from langchain_core.messages import BaseMessage
from openinference.instrumentation.langchain import LangChainInstrumentor
import phoenix as px
from phoenix.otel import register

from .running_agent import run_agent_with_history, make_human_message

# --- Telemetry setup (Phoenix + OpenInference) ---
tracer_provider = register(project_name="agentic-rag-agent4", set_global_tracer_provider=True)
LangChainInstrumentor(tracer_provider=tracer_provider).instrument(skip_dep_check=True)

# Launch Phoenix app (optional; comment if you manage separately)
try:
    session = px.launch_app()
except Exception:
    session = None

# --- Conversation store (sessionized, thread-safe) ---
class ConversationStore:
    """
    Stores histories per session_id, with optional auto reset.
    """
    def __init__(self, auto_reset_threshold: int = 8):
        self._histories: Dict[str, List[BaseMessage]] = {}
        self._lock = RLock()
        self.auto_reset_threshold = auto_reset_threshold

    def get_history(self, session_id: str) -> List[BaseMessage]:
        with self._lock:
            return self._histories.setdefault(session_id, [])

    def append(self, session_id: str, message: BaseMessage) -> int:
        with self._lock:
            hist = self._histories.setdefault(session_id, [])
            hist.append(message)
            length = len(hist)
            if self.auto_reset_threshold and length >= self.auto_reset_threshold:
                # Auto reset after threshold
                self._histories[session_id] = []
            return length

    def reset(self, session_id: str) -> None:
        with self._lock:
            self._histories[session_id] = []

    def size(self, session_id: str) -> int:
        with self._lock:
            return len(self._histories.get(session_id, []))

conversation_store = ConversationStore(auto_reset_threshold=8)

# --- Service facade ---
class AgentService:
    """
    Facade to handle chat requests using sessionized history and run_agent.
    """
    def __init__(self, store: ConversationStore):
        self.store = store

    def chat(self, session_id: str, user_input: str) -> str:
        if not user_input or not user_input.strip():
            return "Please enter a valid message."

        # 1) Append user message
        user_msg = make_human_message(user_input)
        self.store.append(session_id, user_msg)

        # 2) Run agent
        history = self.store.get_history(session_id)
        result = run_agent_with_history(history)

        # 3) Get final assistant message
        answer_msg: BaseMessage = result["messages"][-1]
        # 4) Append assistant message
        self.store.append(session_id, answer_msg)

        # 5) Return content
        return getattr(answer_msg, "content", "")

    def reset(self, session_id: str) -> None:
        self.store.reset(session_id)

    def history_length(self, session_id: str) -> int:
        return self.store.size(session_id)

agent_service = AgentService(conversation_store)
