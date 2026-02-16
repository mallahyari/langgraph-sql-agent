import json
from typing import Literal, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.state.state import AgentState
from app.services.llm import get_openai_client

class VizPlannerOutput(BaseModel):
    """Output schema for the visualization planner."""
    needs_visualization: bool = Field(
        description="Whether the user asked for a visualization or the data is best represented visually."
    )
    visualization_type: Optional[Literal["bar", "line", "pie", "scatter"]] = Field(
        description="Type of chart to generate if needed."
    )
    reasoning: str = Field(description="Why visualization is needed or not.")

async def visualization_planner_node(state: AgentState):
    """
    Decides if a visualization is needed.
    """
    client = get_openai_client()
    
    query_to_use = state.get("refined_query", state["user_query"])
    results = state.get("query_result", [])
    
    # If no results or error, no viz
    if not results or state.get("query_error"):
        return {"needs_visualization": False}
        
    system_prompt = f"""You are a data visualization expert.
    Analyze the user request and data to decide if a chart is necessary.
    
    User Query: {query_to_use}
    Data Sample (first few rows): {str(results[:5])}
    
    Rules:
    1. If user explicitly asks for "plot", "chart", "graph", "visualize", return true.
    2. If the data is a time series or distribution that benefits from visualization, return true.
    3. If the data is a single number or text, return false.
    """
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt}
        ],
        functions=[
            {
                "name": "plan_visualization",
                "description": "Plan the visualization.",
                "parameters": VizPlannerOutput.model_json_schema()
            }
        ],
        function_call={"name": "plan_visualization"},
        temperature=0
    )
    
    tool_call = response.choices[0].message.function_call
    if tool_call:
        arguments = json.loads(tool_call.arguments)
        return {"needs_visualization": arguments.get("needs_visualization", False)}
    
    return {"needs_visualization": False}


async def visualization_generator_node(state: AgentState):
    """
    Generates a Vega-Lite specification for the data.
    """
    client = get_openai_client()
    
    query_to_use = state.get("refined_query", state["user_query"])
    results = state["query_result"]
    
    system_prompt = f"""You are a Vega-Lite expert.
    Generate a valid Vega-Lite JSON specification to visualize the provided data.
    
    User Query: {query_to_use}
    Data: {json.dumps(results)}
    
    Rules:
    1. Return ONLY the JSON object.
    2. Use the 'data' property with 'values' set to the provided data.
    3. Choose appropriate encodings based on the data types.
    4. Add a title and tooltips.
    5. Set "width": "container" to ensure it takes the full available width.
    6. Set "height": 300 for a good aspect ratio.
    7. Enable "autosize": {{ "type": "fit", "contains": "padding" }}.
    """
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    
    try:
        spec = json.loads(response.choices[0].message.content)
        return {"visualization_spec": spec}
    except Exception as e:
        print(f"Error generating viz: {e}")
        return {"visualization_spec": None}
