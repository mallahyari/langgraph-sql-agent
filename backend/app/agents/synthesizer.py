from app.state.state import AgentState
from app.services.llm import get_openai_client

async def response_synthesizer_node(state: AgentState):
    """
    Synthesizes a natural language response based on the query results.
    """
    client = get_openai_client()
    
    user_query = state["user_query"]
    sql_query = state.get("generated_sql", "No SQL generated")
    results = state.get("query_result", [])
    error = state.get("query_error")
    
    if error:
        return {"natural_response": f"I encountered an error while running the query: {error}"}
        
    system_prompt = f"""You are a helpful data assistant.
    Your task is to answer the user's question based on the provided database query results.
    
    User Question: {user_query}
    SQL Query Used: {sql_query}
    Data Results: {results}
    
    Response Guidelines:
    1. Be concise and direct.
    2. If the result is a single number, state it clearly.
    3. If the result is a list, summarize it (e.g., top 5 items).
    4. If the result is empty, politely inform the user.
    5. Do not mention "SQL" or "query" unless necessary for clarity.
    """
    
    # Truncate results if too large to fit in context (naive approach)
    str_results = str(results)
    if len(str_results) > 10000:
        str_results = str_results[:10000] + "... (truncated)"
        
    messages = [{"role": "system", "content": system_prompt}]
    
    # Use LangGraph's native stream writer
    from langgraph.types import StreamWriter
    from langgraph.config import get_stream_writer
    
    writer: StreamWriter = get_stream_writer()
    
    # We can stream tokens directly via writer
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0,
        stream=True
    )
    
    full_response = ""
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            # Write token to the custom stream
            writer(content)
            
    return {"natural_response": full_response}
    
    return {"natural_response": response.choices[0].message.content}
