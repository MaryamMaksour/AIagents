from .agent_tools import get_tools, get_tools_dict
from .prompt import system_prompt
from main.llm import get_llm
 
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
from operator import add as add_messages

llm = get_llm()


tools_dict = get_tools_dict()
llm = llm.bind_tools(get_tools())
print("tools done")


# build the agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# build the agent nodes grapg 
# condition node
def should_continue(state: AgentState):
    """Check if the last message contains tool calls."""
    result = state['messages'][-1]
    return hasattr(result, 'tool_calls') and len(result.tool_calls) > 0


# LLM Agent
def call_llm(state: AgentState) -> AgentState:
    """Function to call the LLM with the current state."""
    messages = list(state['messages'])

    messages =  [SystemMessage(content= system_prompt)] + messages
    print("Function to call the LLM with the current state.")
    
    message = llm.invoke(messages)
    return {'messages': [message]}


# Retriever Agent
def take_action(state: AgentState) -> AgentState:
    """Execute tool calls from the LLM's response."""

    tool_calls = state['messages'][-1].tool_calls
    results = []
    for t in tool_calls:

        if not t['name'] in tools_dict: # Checks if a valid tool is present
            print(f"\nTool: {t['name']} does not exist.")
            result = "Incorrect Tool Name, Please Retry and Select tool from List of Available tools."
        
        else:

          try:
            print(f"Tool Found: {t['name']}. Invoking...")
            if t['name'] == 'get_table_records':
                print(f"Calling Tool: {t['name']} with query: {t['args'].get('query', 'No query provided')}, mx: {t['args'].get('mx', 5)}, table_name:{t['args'].get('table_name', None)}")

                result = tools_dict[t['name']].invoke({"query":t['args'].get('query', ''), "mx":t['args'].get('mx', 5), "table_name":t['args'].get('table_name', None)})
            
            elif t['name'] == "get_ids":
                print(f"Calling Tool: {t['name']} with group_list: {t['args'].get('group_list',[])}, filters_list: {t['args'].get('filters_list', 'No values provided')},  table_name:{t['args'].get('table_name', None)}")
                if t['args'].get('table_name', None) == None:
                    result =  "table name can not be None"
                elif t['args'].get('filters_list', []) == []:
                    result =  "filters_list can not be empty"
                else:    
                    result = tools_dict[t['name']].invoke({"group_list":t['args'].get('group_list', []), "filters_list":t['args'].get('filters_list', []),  "table_name":t['args'].get('table_name', None)})
            
            elif t['name'] == "filters_search":
                print(f"Calling Tool: {t['name']} with group_list: {t['args'].get('group_list',[])}, filters_list: {t['args'].get('filters_list', 'No values provided')},  table_name:{t['args'].get('table_name', None)}, offset:{t['args'].get('offset', 0)}")
                if t['args'].get('table_name', None) == None:
                    result =  "table name can not be None"
                elif t['args'].get('filters_list', []) == []:
                    result =  "filters_list can not be empty"
                else:    
                    result = tools_dict[t['name']].invoke({"group_list":t['args'].get('group_list', []), "filters_list":t['args'].get('filters_list', []),  "table_name":t['args'].get('table_name', None), "offset":t['args'].get('offset', 0)})
            
          except Exception as e:
                result = e

        # Appends the Tool Message
        results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

    print("Tools Execution Complete. Back to the model!")
    return {'messages': results}


# build the graph
graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("retriever_agent", take_action)

graph.add_conditional_edges(
    "llm",
    should_continue,
    {True: "retriever_agent", False: END}
)

graph.add_edge("retriever_agent", "llm")
graph.set_entry_point("llm")

rag_agent = graph.compile()


def run_agent(history : list[BaseMessage] ):
    """Run the RAG Agent with the provided history."""
    return rag_agent.invoke({'messages': history} ) 
