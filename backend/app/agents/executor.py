from app.state.state import AgentState
from app.tools.sql import execute_read_query

def sql_executor_node(state: AgentState):
    """
    Executes the validated SQL query against the database.
    """
    sql_query = state.get("generated_sql")
    
    try:
        results = execute_read_query(sql_query)
        return {"query_result": results, "query_error": None}
    except Exception as e:
        return {"query_result": [], "query_error": str(e)}
