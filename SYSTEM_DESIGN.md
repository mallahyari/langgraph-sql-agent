# SQL Agent System Design

## Overview
An intelligent SQL analytics agent that converts natural language queries into SQL, executes them against a Chinook database, and presents results with visualizations. Features real-time streaming of agent reasoning steps and token-by-token response generation.

## Architecture Components

### 1. Frontend Layer (React + Vite)
**Technology Stack:**
- React 18 with TypeScript
- Tailwind CSS for styling
- Vega-Lite for data visualizations
- Server-Sent Events (SSE) for real-time streaming

**Key Components:**
- **ChatInterface**: Main UI with glassmorphism design
- **ThinkingProcess**: Real-time visualization of agent steps (timeline view)
- **VisualizationRenderer**: Embeds Vega-Lite charts
- **useChat Hook**: Manages SSE connection and state

**Data Flow:**
```
User Input → SSE Connection → Event Stream Parser → UI Updates
                                    ↓
                        [token events, node_update events]
```

### 2. Backend Layer (FastAPI + LangGraph)

#### API Layer
**FastAPI Router** (`/api/chat`)
- Accepts user queries via POST
- Returns StreamingResponse with SSE
- Streams two types of events:
  - `updates`: State changes (SQL, visualizations, node completions)
  - `custom`: Token-by-token text streaming

**Stream Modes:**
```python
stream_mode=["updates", "custom"]
```

#### Agent Orchestration (LangGraph)

**State Management:**
```typescript
AgentState {
  user_query: string
  refined_query: string
  relevance: "relevant" | "irrelevant"
  selected_tables: string[]
  generated_sql: string
  is_valid_sql: boolean
  validation_error: string
  retry_count: number
  query_result: any[]
  natural_response: string
  visualization_spec: object
}
```

**Agent Graph Flow:**
```
START
  ↓
Query Router ──→ [irrelevant] ──→ General Agent ──→ END
  ↓ [relevant]
Query Rewriter
  ↓
Table Selector
  ↓
SQL Generator ←──┐ (retry loop, max 3)
  ↓              │
SQL Validator ───┘ [invalid]
  ↓ [valid]
SQL Executor
  ↓
Response Synthesizer ──→ Visualization Planner ──→ Visualization Generator
  ↓                                                          ↓
END ←────────────────────────────────────────────────────────┘
```

### 3. Agent Nodes

#### Query Router
- **Purpose**: Determines if query is relevant to database domain
- **LLM**: GPT-4
- **Output**: `relevance` ("relevant" | "irrelevant")

#### Query Rewriter
- **Purpose**: Refines user query for clarity
- **LLM**: GPT-4
- **Output**: `refined_query`

#### General Agent
- **Purpose**: Handles out-of-scope queries with helpful guidance
- **LLM**: GPT-4
- **Streaming**: Uses `get_stream_writer()` for token streaming
- **Output**: `natural_response`

#### Table Selector
- **Purpose**: Identifies relevant database tables
- **LLM**: GPT-4
- **Input**: Database schema
- **Output**: `selected_tables`

#### SQL Generator
- **Purpose**: Generates SQL query from natural language
- **LLM**: GPT-4
- **Features**: Self-correction using validation errors
- **Output**: `generated_sql`, increments `retry_count`

#### SQL Validator
- **Purpose**: Validates SQL safety (prevents DROP, DELETE, etc.)
- **Logic**: Regex-based validation
- **Output**: `is_valid_sql`, `validation_error`

#### SQL Executor
- **Purpose**: Executes validated SQL against SQLite database
- **Database**: Chinook (music store data)
- **Output**: `query_result`

#### Response Synthesizer
- **Purpose**: Converts query results into natural language
- **LLM**: GPT-4
- **Streaming**: Uses `get_stream_writer()` for token streaming
- **Output**: `natural_response`

#### Visualization Planner
- **Purpose**: Determines if data should be visualized
- **LLM**: GPT-4
- **Output**: Decision to create visualization

#### Visualization Generator
- **Purpose**: Creates Vega-Lite specification
- **LLM**: GPT-4
- **Output**: `visualization_spec` (JSON)

### 4. Streaming Architecture

**Token Streaming Pattern:**
```python
# In Agent Node
from langgraph.config import get_stream_writer

writer = get_stream_writer()
async for chunk in openai_stream:
    content = chunk.choices[0].delta.content
    writer(content)  # Emits to 'custom' stream
    full_response += content
```

**API Consumption:**
```python
async for mode, payload in graph.astream(inputs, stream_mode=["updates", "custom"]):
    if mode == "updates":
        # Handle state changes (SQL, visualizations, node completions)
    elif mode == "custom":
        # Handle token chunks
```

**Frontend Handling:**
```typescript
if (event.type === 'token') {
    message.content += event.content;  // Append tokens
} else if (event.type === 'node_update') {
    // Update thinking process timeline
}
```

### 5. Data Persistence

**LangGraph Checkpointer:**
- **Type**: SQLite-based MemorySaver
- **Purpose**: Maintains conversation state across requests
- **Thread ID**: Identifies conversation sessions

**Database:**
- **Type**: SQLite (Chinook database)
- **Schema**: Music store (Artists, Albums, Tracks, Customers, Invoices)

### 6. Key Features

**Real-Time Thinking Process:**
- Displays each agent step as it executes
- Timeline visualization with icons and status
- Shows SQL queries and intermediate results

**Token Streaming:**
- Character-by-character response rendering
- Smooth typing effect using native LangGraph streaming
- No custom queue implementation needed

**SQL Validation & Retry:**
- Automatic retry loop (max 3 attempts)
- Self-correction using validation errors
- Prevents unsafe SQL operations

**Premium UI/UX:**
- Glassmorphism design
- Smooth animations and transitions
- Custom scrollbars and hover effects
- Responsive layout

### 7. Technology Stack Summary

**Backend:**
- FastAPI (API framework)
- LangGraph (Agent orchestration)
- OpenAI SDK (LLM interactions)
- SQLite (Database)
- Python 3.13

**Frontend:**
- React 18 + TypeScript
- Vite (Build tool)
- Tailwind CSS (Styling)
- Vega-Lite (Visualizations)
- Lucide React (Icons)

**Infrastructure:**
- SSE for real-time communication
- Context-based streaming (no WebSockets)
- Thread-based conversation management

## Design Principles

1. **No LangChain Dependency**: Direct OpenAI SDK usage for maximum control
2. **Native Streaming**: LangGraph's `get_stream_writer()` for custom data
3. **Separation of Concerns**: Clear boundaries between agents, API, and UI
4. **User Transparency**: Visible agent reasoning process
5. **Graceful Degradation**: Retry loops and fallback responses
6. **Premium Experience**: Modern UI with real-time feedback
