from app.state.state import AgentState
from app.services.llm import get_openai_client
from app.tools.schema import get_database_schema_string

async def sql_generator_node(state: AgentState):
    """
    Generates a SQL query based on the user query and selected table schemas.
    """
    client = get_openai_client()
    
    selected_tables = state["selected_tables"]
    schema_context = get_database_schema_string(selected_tables)
    
    system_prompt = f"""You are an expert SQLite developer.
    Your task is to generate a valid SQLite query to answer the user's question.
    Use the provided schema.
    
    Schema:
    {schema_context}
    
    Rules:
    1. Generate ONLY the SQL query. No markdown formatting, no backticks, no explanation.
    2. The query must be read-only (SELECT).
    3. Use compatible SQLite syntax.
    4. If the user asks for aggregation, use appropriate GROUP BY clauses.
    5. Do not end with a semicolon (optional but cleaner).
    """
    
    query_to_use = state.get("refined_query", state["user_query"])
    validation_error = state.get("validation_error")
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query_to_use}
    ]
    
    if validation_error:
        messages.append({
            "role": "user", 
            "content": f"The previous query was invalid. Error: {validation_error}. Please fix the SQL."
        })
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0
    )
    
    generated_sql = response.choices[0].message.content
    
    # Clean up any potential markdown backticks if the model ignores the instruction
    clean_sql = generated_sql.replace("```sql", "").replace("```", "").strip()
    
    return {
        "generated_sql": clean_sql,
        "retry_count": state.get("retry_count", 0) + 1 if state.get("validation_error") else 0
    }
