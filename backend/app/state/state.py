import operator
from typing import Annotated, List, Optional, TypedDict, Any, Dict

class AgentState(TypedDict):
    """Global state for the SQL agent workflow."""
    
    # User input
    user_query: str
    refined_query: Optional[str]  # Rewritten query to remove ambiguity
    
    # Workflow logic
    relevance: str  # "relevant" or "irrelevant"
    selected_tables: List[str]
    
    # SQL Generation & Execution
    generated_sql: str
    query_result: List[Dict[str, Any]]
    query_error: Optional[str]
    is_valid_sql: bool
    retry_count: int = 0
    validation_error: Optional[str]
    
    # Final Output
    natural_response: str
    visualization_spec: Optional[Dict[str, Any]]
    needs_visualization: bool
    
    # Logging
    logs: Annotated[List[str], operator.add]
    steps: Annotated[List[str], operator.add]
