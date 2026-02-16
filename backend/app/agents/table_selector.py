import json
from typing import List
from pydantic import BaseModel, Field

from app.state.state import AgentState
from app.services.llm import get_openai_client
from app.tools.sql import get_table_names

class TableSelectorOutput(BaseModel):
    """Output schema for the table selector agent."""
    selected_tables: List[str] = Field(
        description="List of table names that are relevant to the user query."
    )

async def table_selector_node(state: AgentState):
    """
    Selects the relevant tables for the user query from the database schema.
    """
    client = get_openai_client()
    
    all_tables = get_table_names()
    formatted_tables = ", ".join(all_tables)
    
    # Use refined query if available, closely matching the user intent
    query_to_use = state.get("refined_query", state["user_query"])
    
    system_prompt = f"""You are an expert database architect.
    Your task is to select the most relevant tables from the database to answer the user's query.
    The available tables are: {formatted_tables}.
    Return a list of ONLY the table names that are strictly necessary.
    Do not halluncinate table names.
    """
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query_to_use}
        ],
        functions=[
            {
                "name": "select_tables",
                "description": "Select relevant tables.",
                "parameters": TableSelectorOutput.model_json_schema()
            }
        ],
        function_call={"name": "select_tables"}
    )
    
    tool_call = response.choices[0].message.function_call
    selected = []
    
    if tool_call:
        try:
            arguments = json.loads(tool_call.arguments)
            selected = arguments.get("selected_tables", [])
        except json.JSONDecodeError:
            selected = []
            
    # Filter out any hallucinates tables basically
    valid_tables = [t for t in selected if t in all_tables]
    
    return {"selected_tables": valid_tables}
