import re
from typing import Tuple

FORBIDDEN_KEYWORDS = [
    "DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "ALTER", "GRANT", "REVOKE"
]

def validate_sql_safety(query: str) -> Tuple[bool, str]:
    """
    Validates that the SQL query is read-only and safe to execute.
    Returns (is_safe, error_message).
    """
    # Normalize query
    normalized = query.upper()
    
    # Check for forbidden keywords
    for keyword in FORBIDDEN_KEYWORDS:
        # Check for keyword as a whole word
        if re.search(r'\b' + keyword + r'\b', normalized):
            return False, f"SQL query contains forbidden keyword: {keyword}. Only read-only queries are allowed."
            
    # Basic check for semicolon at end (optional, sqlite handles it but good practice)
    # if not query.strip().endswith(';'):
    #     return False, "Query must end with a semicolon."
        
    return True, ""
