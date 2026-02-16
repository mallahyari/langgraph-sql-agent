import json
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field
from app.state.state import AgentState
from app.services.llm import get_openai_client

class RouterOutput(BaseModel):
    """Output schema for the router agent."""
    relevance: Literal["relevant", "irrelevant"] = Field(
        description="Whether the user query is relevant to a music store database (Chinook) or distribution analytics."
    )

async def query_router_node(state: AgentState):
    """
    Analyzes the user query to determine if it's relevant to the database.
    Now uses OpenAI direct client.
    """
    client = get_openai_client()
    
    system_prompt = """You are an expert at routing user queries.
    Your task is to determine if the user's query is relevant to a music store database (Chinook) or distribution analytics.
    The database contains information about artists, albums, tracks, invoices, customers, and employees.
    If the query is greeting, chitchat, or unrelated to the data, mark it as 'irrelevant'.
    Otherwise, mark it as 'relevant'.
    """
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": state["user_query"]}
        ],
        functions=[
            {
                "name": "route_query",
                "description": "Route the user query based on relevance.",
                "parameters": RouterOutput.model_json_schema()
            }
        ],
        function_call={"name": "route_query"}
    )
    
    # Check if function call exists
    tool_call = response.choices[0].message.function_call
    if tool_call:
        arguments = json.loads(tool_call.arguments)
        return {"relevance": arguments.get("relevance", "irrelevant")}
    
    return {"relevance": "irrelevant"}
