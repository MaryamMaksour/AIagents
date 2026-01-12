
from typing import Optional
import uuid
import requests
from langchain_core.tools import tool

  

@tool
def property_TOOL( query: str, session_id: str = "agents:agent1-subsession",  CHAT_ENDPOINT_AGENT1 = "http://localhost:8001/chat"):
   
    """
    Calls Agent 1's chat endpoint to get answers about Projects, Developers, Buildings, or Units.

    Args:
        query: The sub-question to delegate to Agent 1. 

    Returns:
        A plain string answer from Agent 1, or a string starting with [agent1_service_error] on failure.
    """
    if not query or not str(query).strip():
        return "[agent1_service_error] query cannot be None or empty."

    # Decide whether to share Agent4's session or isolate
    forwarded_session = session_id

    payload = {
        # Match Agent1’s expected schema: if it expects "message", change here accordingly.
        "session_id": forwarded_session,
        "user_input": "agent call for : "+str(query),
    }

    headers = {"Content-Type": "application/json"}
  
    try:
        resp = requests.post(CHAT_ENDPOINT_AGENT1, json=payload, headers=headers, timeout=3600)
        resp.raise_for_status()
        data = resp.json()

        # Be defensive with response shape
        # Your earlier services returned {"answer": "..."} or {"Message": "..."}
        answer = data.get("answer") or data.get("Message")
        if not answer:
            # Fallback to whole JSON if no 'answer' key exists
            return f"[agent1_service_error] Agent1 returned no 'answer'. Raw: {data}"
        return str(answer)

    except requests.Timeout:
        return "[agent1_service_error] Timeout talking to Agent1."
    except requests.RequestException as e:
        return f"[agent1_service_error] HTTP failure: {e}"
    except Exception as e:
        return f"[agent1_service_error] Unexpected: {e}"


@tool
def DEALS_TOOL( query: str, session_id: str = "agents:agent4-subsession",  CHAT_ENDPOINT_AGENT4 = "http://localhost:8004/chat"):
   
    """
    Calls Agent 4's chat endpoint to get answers about Deals.

    Args:
        query: The sub-question to delegate to Agent 4.

    Returns:
        A plain string answer from Agent 4, or a string starting with [agent4_service_error] on failure.
    """
    if not query or not str(query).strip():
        return "[agent4_service_error] query cannot be None or empty."

    # Decide whether to share Agent4's session or isolate
    forwarded_session = session_id

    payload = {
        # Match Agent1’s expected schema: if it expects "message", change here accordingly.
        "session_id": forwarded_session,
        "user_input": "agent call for : "+str(query),
    }

    headers = {"Content-Type": "application/json"}
  
    try:
        resp = requests.post(CHAT_ENDPOINT_AGENT4, json=payload, headers=headers, timeout=36)
        resp.raise_for_status()
        data = resp.json()

        # Be defensive with response shape
        # Your earlier services returned {"answer": "..."} or {"Message": "..."}
        answer = data.get("answer") or data.get("Message")
        if not answer:
            # Fallback to whole JSON if no 'answer' key exists
            return f"[agent1_service_error] Agent1 returned no 'answer'. Raw: {data}"
        return str(answer)

    except requests.Timeout:
        return "[agent1_service_error] Timeout talking to Agent1."
    except requests.RequestException as e:
        return f"[agent1_service_error] HTTP failure: {e}"
    except Exception as e:
        return f"[agent1_service_error] Unexpected: {e}"



tools = [property_TOOL, DEALS_TOOL]
tools_dict = {our_tool.name: our_tool for our_tool in tools} # Creating a dictionary of our tools

def get_tools():
   return tools

def get_tools_dict():
   return tools_dict


