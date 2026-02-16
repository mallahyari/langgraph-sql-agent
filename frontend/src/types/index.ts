export interface AgentEvent {
    type: 'start' | 'end' | 'tool_start' | 'tool_end' | 'node_update' | 'error' | 'token';
    data?: any;
    name?: string;
    input?: any;
    output?: any;
    node?: string;
    response?: string;
    visualization?: any;
    sql?: string;
    error?: string;
    content?: string;
}

export interface Message {
    role: 'user' | 'assistant';
    content: string;
    visualization?: any;
    sql?: string;
    trace?: AgentEvent[];
}
