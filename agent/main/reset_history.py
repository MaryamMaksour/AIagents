from main.llm import get_llm
from main.config import OLLAMA_MAX_WINDOW_TOKENS


llm = get_llm()

def reset_history(history):
    history_msg = ""

    for msg in history:
        history_msg += msg.content + " " 

    system_prompt = f"""you are the best LLM in summary content for QA between user and other LLM , 
                        summary it to save token so keep only content usefull information without any metadata .if the list empty return empty string {history_msg} return the suumary as text""" 
    return llm.invoke(system_prompt)

def history_need_reset(history):
    """ tool the count number of token consumed so far"""
    history_msg = ""

    for msg in history:
        history_msg += msg.content + " " 
  
    history_words_couont = len(history_msg.split())
    
    tokens_percentage = (history_words_couont / int(OLLAMA_MAX_WINDOW_TOKENS)) * 100 # % of history included

    return tokens_percentage >= 40.00

