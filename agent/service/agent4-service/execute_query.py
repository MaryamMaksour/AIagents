
from typing import List, Optional 
from main.conect_to_DB import conect_to_DB
from main.embeddings import embed_query
from psycopg2 import sql

 
def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
        
        return "Connection already established."
    
    wrapper.has_run = False
    return wrapper


@run_once
def conect():
    return conect_to_DB()

connection = conect()
cur = connection.cursor()




word_search_list = [ 'type', 'stage', "department","status", "city", "country" ]

semantic_search_list = [ "name", "nationality" , "address", "role", "position" ,   
                         "section" ]
numaric_search_list = []

id_col_list = { "deals": ["id", "directorid", "agentid","unitid"] }
ALLOWED_OPS = {
            '=': sql.SQL('='),
            '!=': sql.SQL('!='),
            '<': sql.SQL('<'),
            '<=': sql.SQL('<='),
            '>': sql.SQL('>'),
            '>=': sql.SQL('>='),
            'LIKE': sql.SQL('LIKE'),
            'ILIKE': sql.SQL('ILIKE'),
        }

aggregation = ['max', 'min', 'count', 'sum']

def vector_to_literal(vec):
    # Produces a string like: "[0.123, -0.456, 0.0, ...]"
    return "[" + ", ".join(str(float(x)) for x in vec) + "]"

def Id_list( table):

    return id_col_list[table]
    
def word_search(filters_list, table):
    word_part = []
    word_params = []

    for col, values in filters_list:
       word_part.append(
                sql.SQL(" {col} = ANY (%s)").format(col = sql.Identifier(col))
            )
       vs = [str(v) for v in values]
       word_params.append(vs)

    return word_part, word_params

def semantic_search(filters_list, table):
     
     order_params = []
     dist_terms = []

     # Semantic ranking columns
     for col, values in filters_list:
            if (col in ("shortname", "name")) and (table in ("buildings", "projects")):
                embed_cols = ["embed_name", "embed_shortname"]
            else:
                embed_cols = [f"embed_{col}"]

            # Build one distance term per (embed_col, value) pair
            for embed_col in embed_cols:
                for v in values:
                    vec_embed = embed_query(v)  # must return a list[float] of correct dimension

                    term = sql.SQL("{c} <=> %s::vector < 0.35").format(c=sql.Identifier(embed_col))
                    order_params.append(vector_to_literal(vec_embed))

                    dist_terms.append(term)

     return order_params, dist_terms

def numaric_search(filters_list, table):
    where_parts = []
    where_params = []

    for col, values, ops in filters_list:
        op = ops.strip()
        
        if len(values) > 1:
             # check if values are integers
            for v in values:
                if v is None or (not str(v).isdigit()):
                    return where_params, where_parts
            
            where_parts.append(
                sql.SQL("{col} '{op}' ANY(%s)").format(col=sql.Identifier(col), op=sql.Identifier(op))
            )
            if col != 'id':
                where_params.append([str(v) for v in values])
            else:
                where_params.append(values)
        else:
            
            where_parts.append(
                sql.SQL("{col} {op} %s").format(col=sql.Identifier(col), op= ALLOWED_OPS[op])
            )
            if col != 'id':
                where_params.append(str(values[0]))
            else:
                where_params.append(values[0])
      
            
    return where_params, where_parts
    
 
def filters( group_list,   filters_list, table, OFFSET=0, LIMIT=5):
    try:
        table = table.lower()
    except:
        table = table[0].lower()
    """
    group_list: list[str] to use in DISTINCT
    filters_list: list[tuple[str, list, str]]  e.g. [("floor", ["3"], "="), ("tags", ["on see"], "="), ("price", ["30000"], "<")]
    
    table: str table name (e.g., "buildings")
    OFFSET/LIMIT: pagination
     """
    
   
    # word | numaric search
    where_parts = []
    where_params = []

    word_part = []
    word_params = []

    #semantic search
    dist_terms = []
    order_params = []

    
    word = []
    semantic = []
    numaric = []

    for col, values, ops in filters_list:
        if not values:
            return {"rows": [f"values can not be empty for col {col}"], "row_count": 0}

        col_norm = col.lower()

        if col_norm  in numaric_search_list:
            numaric.append([col_norm, values, ops])
        elif col_norm in semantic_search_list:
            semantic.append([col_norm, values])
        else:
            word.append([col_norm, values])


        if semantic:
            order_params, dist_terms = semantic_search(semantic, table)
        if word:
            word_part, word_params = word_search(word, table)
        if numaric:
            where_params, where_parts = numaric_search(numaric, table)

    where_params += word_params
    where_parts  += word_part

    where_params += order_params
    where_parts  += dist_terms

    gl_ls = [ ]
    
    for col  in group_list:
        col_norm = col.lower()

        gl_ls.append(sql.SQL(" DISTINCT {col} ").format(col = sql.Identifier(col_norm))) 
     
    text_select = gl_ls.copy()
    text_select.append(sql.SQL("row_txt"))

    count_select = gl_ls.copy()
    
    
    if not count_select:
        count_select.append( sql.SQL("*") )

   


    count_query = sql.SQL(" SELECT count (") + sql.SQL(", ").join(count_select) + sql.SQL(" ) from {tbl} ").format(tbl = sql.Identifier(table))
    text_query  = sql.SQL(" SELECT ") + sql.SQL(", ").join(text_select)  + sql.SQL(" from {tbl} ").format(tbl = sql.Identifier(table))
 

    data_params = []
    if where_parts:
        data_params.extend(where_params)
        text_query = text_query + sql.SQL(" WHERE ") + sql.SQL(" AND ").join(where_parts)
        count_query = count_query + sql.SQL(" WHERE ") + sql.SQL(" AND ").join(where_parts)
  
   
    try:
        # get the count
        cur.execute(count_query, tuple(data_params))
        cnt_rows = cur.fetchall()


        
        # get row text
        text_query = text_query + sql.SQL(" LIMIT %s OFFSET %s")
        data_params.extend([ int(LIMIT), int(OFFSET)])

        cur.execute(text_query, tuple(data_params))
        rows_data = cur.fetchall()
    

        return {"sample_text": rows_data, "row_count": cnt_rows[0][0]}
    except Exception as e:
         connection.rollback()
         connection.commit()
         return {"sample_text": [f"SQL error: {str(e)}"], "row_count": 0}


def get_ids_list(group_list,  filters_list, table ):
    try:
        table = table.lower()
    except:
        table = table[0].lower()
    """
    group_list: list[str]
    filters_list: list[tuple[str, list, str]]  e.g. [("floor", ["3"], "="), ("tags", ["on see"], "="), ("price", ["30000"], "<")]
    
    table: str table name (e.g., "buildings")
    OFFSET/LIMIT: pagination
     """
    
   
    # word | numaric search
    where_parts = []
    where_params = []

    word_part = []
    word_params = []

    #semantic search
    dist_terms = []
    order_params = []

    
    word = []
    semantic = []
    numaric = []

    for col, values, ops in filters_list:
        if not values:
            return {"rows": [f"values can not be empty for col {col}"], "row_count": 0}

        col_norm = col.lower()

        if col_norm  in numaric_search_list:
            numaric.append([col_norm, values, ops])
        elif col_norm in semantic_search_list:
            semantic.append([col_norm, values])
        else:
            word.append([col_norm, values])


        if semantic:
            order_params, dist_terms = semantic_search(semantic, table)
        if word:
            word_part, word_params = word_search(word, table)
        if numaric:
            where_params, where_parts = numaric_search(numaric, table)

    where_params += word_params
    where_parts  += word_part

    where_params += order_params
    where_parts  += dist_terms

    id_col_list = [sql.Identifier(col)   for col in Id_list( table)]

  
    id_select = [ ]
    
    for col  in group_list:
        col_norm = col.lower()

        id_select.append(sql.SQL(" DISTINCT ({col}) ").format(col = sql.Identifier(col_norm))) 
    
     

  
    if not id_select:
        id_select.append( sql.SQL("id") )

 
    count_query = sql.SQL(" SELECT count (") + sql.SQL(", ").join(id_select) + sql.SQL(" ) from {tbl} ").format(tbl = sql.Identifier(table))
    id_query = sql.SQL(" SELECT ") + sql.SQL(", ").join(id_select) + sql.SQL(" from {tbl} ").format(tbl = sql.Identifier(table))

    data_params = []
    if where_parts:
        data_params.extend(where_params)
        count_query = count_query + sql.SQL(" WHERE ") + sql.SQL(" AND ").join(where_parts)
        id_query = id_query + sql.SQL(" WHERE ") + sql.SQL(" AND ").join(where_parts)
 

     
    try:
    # get the count
        cur.execute(count_query, tuple(data_params))
        cnt_rows = cur.fetchall()

        # get id rows
        cur.execute(id_query, tuple(data_params))
        id_data = cur.fetchall()



        return { "id_col_name": id_col_list, "ids": id_data, "table_name":table, "row_count": cnt_rows[0][0] }
    except Exception as e:
         connection.rollback()
         connection.commit()
         return {"id_col_name": [f"SQL error: {str(e)}"], "ids": [], "table_name": table, "row_count": 0}




def table_records(
    query_text: str,
    table: str,   # filter by logical table name if provided
    max_number_of_res_points: int = 8,
    embedding_col: str = "embedding",
    text_col: str = "row_txt",
    ):
    """
    Semantic search over the records table using pgvector distance.
    """
    query_vec = embed_query(query_text)
    max_number_of_res_points = max(5, min(10, max_number_of_res_points))

 
    sql = f""" SELECT {text_col}
                From {table}
                ORDER BY {embedding_col} <=> '{query_vec}'
                LIMIT 8
                   """

    try:

        cur.execute(sql)
        rows = cur.fetchall() 
        connection.rollback()
        connection.commit()

        return rows
    except Exception as e:
         connection.rollback()
         connection.commit()
         return ["SQL error"+str(e)]   

 
print(filters( [],   [['Status', ['Active'], '='], ['UnitId', ['1577', '1578', '1579', '1580', '1581', '1582', '1583', '1584', '1585', '1586', '1587', '1588', '1589', '1590', '1591', '1592', '1593', '1594', '1595', '1596', '1597', '1598', '1599', '1600', '1603', '1604', '1605', '1606', '1607', '1608', '1609', '1610', '1611', '1612', '1613', '1614', '1615', '1616', '1617', '1618', '1619', '1620', '1621', '1622', '1623', '1624', '1625', '1626', '1627', '1628', '1629', '1630', '1631', '1632', '1633', '1634', '1635', '1636', '1637', '1638', '1639', '1640', '1641', '1601', '1602'], '=']], "Deals", OFFSET=0, LIMIT=5))