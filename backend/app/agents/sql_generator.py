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
    6. IMPORTANT: When using UNION or UNION ALL, ORDER BY must come AFTER all SELECT statements, not between them.
       CORRECT: (SELECT ...) UNION ALL (SELECT ...) ORDER BY column
       INCORRECT: (SELECT ... ORDER BY column) UNION ALL (SELECT ... ORDER BY column)
    """
    
    query_to_use = state.get("refined_query", state["user_query"])
    validation_error = state.get("validation_error")
    query_error = state.get("query_error")
    retry_count = state.get("retry_count", 0)
    
    # Debug logging
    print(f"[SQL Generator] Retry count: {retry_count}")
    print(f"[SQL Generator] Validation error: {validation_error}")
    print(f"[SQL Generator] Query error: {query_error}")
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query_to_use}
    ]
    
    # Add error feedback for retry
    if validation_error:
        error_msg = f"The previous query failed validation. Error: {validation_error}. Please fix the SQL."
        print(f"[SQL Generator] Adding validation error to prompt: {error_msg}")
        messages.append({
            "role": "user", 
            "content": error_msg
        })
    elif query_error:
        error_msg = f"The previous query failed during execution. Error: {query_error}. Please fix the SQL syntax. Remember: ORDER BY must come AFTER UNION ALL, not before."
        print(f"[SQL Generator] Adding query error to prompt: {error_msg}")
        messages.append({
            "role": "user",
            "content": error_msg
        })
    
    # Use higher temperature on retries to get different solutions
    temperature = 0.3 if (validation_error or query_error) else 0
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=temperature
    )
    
    generated_sql = response.choices[0].message.content
    
    # Clean up any potential markdown backticks if the model ignores the instruction
    clean_sql = generated_sql.replace("```sql", "").replace("```", "").strip()
    
    print(f"[SQL Generator] Generated SQL: {clean_sql[:100]}...")
    
    # Increment retry count if there was an error
    should_increment = bool(validation_error or query_error)
    
    return {
        "generated_sql": clean_sql,
        "retry_count": state.get("retry_count", 0) + 1 if should_increment else 0
    }
