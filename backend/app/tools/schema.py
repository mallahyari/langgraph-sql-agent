from typing import List, Dict
from app.tools.sql import get_table_names, get_table_schema

def get_database_schema_string(table_names: List[str] = None) -> str:
    """
    Returns a formatted string containing the schema for the specified tables.
    If no tables are specified, returns schema for all tables.
    """
    if not table_names:
        table_names = get_table_names()
    
    schema_parts = []
    for table in table_names:
        schema = get_table_schema(table)
        if schema:
            schema_parts.append(schema)
            
    return "\n\n".join(schema_parts)

def get_all_table_names_formatted() -> str:
    """Returns a comma-separated string of all table names."""
    return ", ".join(get_table_names())
