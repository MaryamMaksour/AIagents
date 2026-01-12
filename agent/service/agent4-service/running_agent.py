
# app/agent_runner.py
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, BaseMessage

# Import your real agent implementation
from .RAG_Agent import run_agent  

def run_agent_with_history(history: List[BaseMessage]) -> Dict[str, Any]:
    """
    Thin wrapper to run your agent and return a standardized dict.
    Expected result structure: {'messages': [BaseMessage, ...]}
    """
    result = run_agent(history)
    if not isinstance(result, dict) or "messages" not in result or not result["messages"]:
        raise ValueError("Agent returned invalid structure; expected dict with 'messages' list.")
    return result

def make_human_message(content: str) -> HumanMessage:
    return HumanMessage(content=content)


