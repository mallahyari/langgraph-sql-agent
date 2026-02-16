from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio

from app.graph.graph import app_graph

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default_thread"

async def event_generator(user_message: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    inputs = {"user_query": user_message}
    
    try:
        yield f"data: {json.dumps({'type': 'start', 'data': 'Workflow started'})}\n\n"

        async for mode, payload in app_graph.astream(inputs, config=config, stream_mode=["updates", "custom"]):
            if mode == "updates":
                for node_name, state_update in payload.items():
                    # Handle state updates (thinking process, visualizations, etc.)
                    event_payload = {"type": "node_update", "node": node_name}
                    
                    if isinstance(state_update, dict):
                        if "natural_response" in state_update:
                            event_payload["response"] = state_update["natural_response"]
                        
                        if "visualization_spec" in state_update:
                            event_payload["visualization"] = state_update["visualization_spec"]
                            
                        if "generated_sql" in state_update:
                            event_payload["sql"] = state_update["generated_sql"]
                        
                        if "query_result" in state_update:
                            try:
                                event_payload["data"] = state_update["query_result"]
                            except:
                                event_payload["data"] = str(state_update["query_result"])

                    yield f"data: {json.dumps(event_payload)}\n\n"
                    
            elif mode == "custom":
                # Handle custom token stream
                yield f"data: {json.dumps({'type': 'token', 'content': payload})}\n\n"
        
        yield f"data: {json.dumps({'type': 'end', 'data': 'Workflow finished'})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    return StreamingResponse(
        event_generator(request.message, request.thread_id),
        media_type="text/event-stream"
    )
