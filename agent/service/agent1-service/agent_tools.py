
from langchain_core.tools import tool
from .execute_query import table_records,filters, get_ids_list


@tool
def get_table_records(query: str, table_name:str, mx:int) -> str:
    """
    Uses semantic search to retrieve the parts of knowledge base that could be most relevant to answer your query (Use the affirmative form rather than a question.).
    and take the max number of result points as input
    1. query:string the query string to search for relevant information.
    2. table_name: string the table name to search on it
    2. mx:int maximum number of result points to retrieve. between 3, 10
    Returns:
        - A string containing the relevant information retrieved from the tables.
 
    """

    mx = max(3, min(mx, 10))  # Ensure mx is between 3 and 10
    docs = table_records(query, table_name, max_number_of_res_points=mx)

    if not docs:
      return "I found no relevent information in this tables"

    results = []

    for i , doc in enumerate(docs):
      results.append(f"record {i+1}, record {doc}")
    
    results = " | ".join(results)

    return results
 

 
@tool
def filters_search(group_list: list, filters_list: list, table_name: str, offset: int):
  
   """
    filter with AND logic and pagination (5 rows/page). 

    Input
    - group_list: [column_name_to_group_by:str, ....]  # columns to use it in DISTINCT; may be empty for no grouping
        • Example: ["BuildingId"] on table="Units" returns one row per distinct BuildingId .
    - filters_list: list of list [ [column_name:str, [values...], operator for this values: str], ...]
        • All columns must belong to `table_name`.
        • operator ∈ {"=", "!=", "<", ">", "<=", ">=", "LIKE", "ILIKE"}; values are list of strings (Id as PK is int).
    - table_name: str
    - offset: int 

    Output:
      {"sample_text": <text for up to 5 rows/groups from offset>, "row_count": : <total matches>}

   """

   res = filters( group_list, filters_list, table_name, offset)
   docs = res['sample_text']
    

   if not docs:
      return "error. This may be due to an incorrect value, an invalid table name, or the absence of relevant data in the selected tables. Please try get_table_records tool or adjust the input values if the input value number send it as integer not string." 
    
   return res


@tool
def get_ids(group_list: list, filters_list: list, table_name: str ):
  
   """
    return all ids match the filters.

    Input
    - group_list: [column_name_to_group_by:str, ....]  # columns to use it in DISTINCT; may be empty for no grouping
        • Example: ["BuildingId"] on table="Units" returns one row per distinct BuildingId .
    - filters_list: list of list [ [column_name:str, [values...], operator for this values: str], ...]
        • All columns must belong to `table_name`.
        • operator ∈ {"=", "!=", "<", ">", "<=", ">=", "LIKE", "ILIKE"}; values are list of strings (Id as PK is int).
    - table_name: str
    - offset: int 

    Output:
        return { "id_col_name": list of id column names to match ids parameter, "ids": list of tuple of all ids ,"table_name":tabel_name , "row_count":<total matches>  }


   """

   res = get_ids_list( group_list, filters_list, table_name) 
   docs = res['ids']
    

   if not docs:
      return "error. This may be due to an incorrect value, an invalid table name, or the absence of relevant data in the selected tables. Please try get_table_records tool or adjust the input values if the input value number send it as integer not string." 
    
   return res



tools = [get_table_records,filters_search, get_ids]
tools_dict = {our_tool.name: our_tool for our_tool in tools} # Creating a dictionary of our tools

def get_tools():
   return tools

def get_tools_dict():
   return tools_dict


