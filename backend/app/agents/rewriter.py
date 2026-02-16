from app.state.state import AgentState
from app.services.llm import get_openai_client

async def query_rewriter_node(state: AgentState):
    """
    Rewrites the user query to be more specific and SQL-friendly.
    """
    client = get_openai_client()
    
    user_query = state["user_query"]
    
    system_prompt = """You are an expert SQL analyst. 
    Your task is to rewrite the user's query to make it clearer, less ambiguous, and easier to translate into SQL.
    
    Rules:
    1. Resolve vague terms (e.g., "best" -> "top by sales/count", "popular" -> "highest number of purchases").
    2. Maintain the user's original intent.
    3. If the query is already clear, return it as is.
    4. Do not add any conversational filler.
    5. Ensure the rewritten query implies the necessary aggregations if applicable (e.g. "by year", "by country").
    
    Example:
    Input: "Show me sales"
    Output: "Show total sales revenue for each year"
    
    Input: "best customers"
    Output: "Show top 10 customers by total purchase amount"
    """
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=0
    )
    
    refined_query = response.choices[0].message.content
    
    return {"refined_query": refined_query}
