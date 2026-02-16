from app.state.state import AgentState
from app.tools.validator import validate_sql_safety

def sql_validator_node(state: AgentState):
    """
    Validates the generated SQL for safety.
    """
    sql_query = state.get("generated_sql", "")
    is_safe, error_message = validate_sql_safety(sql_query)
    
    return {
        "is_valid_sql": is_safe,
        "validation_error": error_message if not is_safe else None,
        "query_error": None  # Clear execution errors when re-validating
    }
