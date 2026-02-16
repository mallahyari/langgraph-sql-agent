from app.state.state import AgentState
from app.services.llm import get_openai_client

async def general_agent_node(state: AgentState):
    """
    Handles queries that are not relevant to the specific database domain.
    Provides a helpful response and guides the user back to the supported topics.
    """
    client = get_openai_client()
    user_query = state["user_query"]
    
    system_prompt = """You are a helpful assistant for a Distribution Analytics application based on the Chinook music store database.
    The user has asked a question that is outside the scope of this database.
    
    Your task is to:
    1. Politely acknowledge the user's query.
    2. Explain that you specialize in analyzing the Chinook music store data (Sales, Customers, Tracks, Artists, Invoices).
    3. Suggest 2-3 relevant questions they could ask instead.
    
    Keep the tone professional and helpful.
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    # Use LangGraph's native stream writer
    from langgraph.types import StreamWriter
    from langgraph.config import get_stream_writer

    writer: StreamWriter = get_stream_writer()

    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
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
