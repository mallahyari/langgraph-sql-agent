from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.state.state import AgentState
from app.agents.router import query_router_node
from app.agents.router import query_router_node
from app.agents.rewriter import query_rewriter_node
from app.agents.general import general_agent_node
from app.agents.table_selector import table_selector_node
from app.agents.sql_generator import sql_generator_node
from app.agents.validator import sql_validator_node
from app.agents.executor import sql_executor_node
from app.agents.synthesizer import response_synthesizer_node
from app.agents.visualization import visualization_planner_node, visualization_generator_node

# Define Graph
workflow = StateGraph(AgentState)

# Add Nodes
# Add Nodes
workflow.add_node("query_router", query_router_node)
workflow.add_node("query_rewriter", query_rewriter_node)
workflow.add_node("general_agent", general_agent_node)
workflow.add_node("table_selector", table_selector_node)
workflow.add_node("sql_generator", sql_generator_node)
workflow.add_node("sql_validator", sql_validator_node)
workflow.add_node("sql_executor", sql_executor_node)
workflow.add_node("response_synthesizer", response_synthesizer_node)
workflow.add_node("visualization_planner", visualization_planner_node)
workflow.add_node("visualization_generator", visualization_generator_node)

# Add Entry Point
workflow.set_entry_point("query_router")

# Conditional Edges

def router_edge(state: AgentState):
    if state["relevance"] == "irrelevant":
        return "general_agent"
    return "query_rewriter"

def validator_edge(state: AgentState):
    if state["is_valid_sql"]:
        return "sql_executor"
    else:
        # Check retry count (default max 3)
        if state.get("retry_count", 0) < 3:
            return "sql_generator"
        return "end"

def visualization_edge(state: AgentState):
    if state.get("needs_visualization"):
        return "visualization_generator"
    return "end"

workflow.add_conditional_edges(
    "query_router",
    router_edge,
    {
        "general_agent": "general_agent",
        "query_rewriter": "query_rewriter"
    }
)

workflow.add_edge("query_rewriter", "table_selector")
workflow.add_edge("table_selector", "sql_generator")
workflow.add_edge("sql_generator", "sql_validator")

workflow.add_conditional_edges(
    "sql_validator",
    validator_edge,
    {
        "sql_executor": "sql_executor",
        "sql_generator": "sql_generator",
        "end": END
    }
)

workflow.add_edge("sql_executor", "response_synthesizer")
workflow.add_edge("response_synthesizer", "visualization_planner")

workflow.add_conditional_edges(
    "visualization_planner",
    visualization_edge,
    {
        "visualization_generator": "visualization_generator",
        "end": END
    }
)

workflow.add_edge("visualization_generator", END)
workflow.add_edge("general_agent", END)

# Compile
# Checkpointer for persistence (using MemorySaver for now, could be Postgres)
checkpointer = MemorySaver()
app_graph = workflow.compile(checkpointer=checkpointer)
