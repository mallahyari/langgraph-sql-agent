import React, { useEffect, useRef } from 'react';
import type { AgentEvent } from '../types';
import { cn } from '../lib/utils';
import { CheckCircle2, Circle, Clock, AlertCircle, ArrowRight, Table, Code2, BrainCircuit } from 'lucide-react';

interface TraceMonitorProps {
    events: AgentEvent[];
}

export const TraceMonitor: React.FC<TraceMonitorProps> = ({ events }) => {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (events.length > 0) {
            bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [events]);

    if (events.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-gray-400 p-8 text-center space-y-4">
                <BrainCircuit className="w-12 h-12 opacity-20" />
                <p className="text-sm">Agent activity will appear here...</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col space-y-4 p-4 text-xs">
            {events.map((event, index) => (
                <div key={index} className="relative pl-4 border-l-2 border-gray-100 last:border-transparent animate-in slide-in-from-left-2 fade-in duration-300">
                    {/* Timeline dot */}
                    <div className="absolute -left-[5px] top-0 bg-white">
                        {event.type === 'start' && <Circle className="w-2.5 h-2.5 text-blue-500 fill-current" />}
                        {event.type === 'end' && <CheckCircle2 className="w-2.5 h-2.5 text-green-500" />}
                        {event.type === 'error' && <AlertCircle className="w-2.5 h-2.5 text-red-500" />}
                        {(event.type === 'tool_start' || event.type === 'node_update') && <div className="w-2.5 h-2.5 rounded-full bg-gray-300 ring-2 ring-white" />}
                    </div>

                    <div className="flex flex-col space-y-1">
                        <div className="flex items-center justify-between">
                            <span className={cn(
                                "font-semibold uppercase tracking-wider text-[10px]",
                                event.type === 'error' ? "text-red-600" : "text-gray-500"
                            )}>
                                {event.node || event.name || event.type?.replace('_', ' ')}
                            </span>
                            <span className="text-[10px] text-gray-300">{index + 1}</span>
                        </div>

                        {/* Content based on event type */}
                        {event.sql && (
                            <div className="p-2 bg-slate-900 border border-slate-800 rounded text-green-400 font-mono overflow-x-auto shadow-sm">
                                <div className="flex items-center text-[10px] text-slate-500 mb-1 border-b border-slate-800 pb-1">
                                    <Code2 className="w-3 h-3 mr-1" /> SQL Query
                                </div>
                                {event.sql}
                            </div>
                        )}

                        {event.input && (
                            <div className="p-2 bg-gray-50 border border-gray-100 rounded text-gray-600 overflow-hidden">
                                <div className="flex items-center text-[10px] text-gray-400 mb-1">
                                    <ArrowRight className="w-3 h-3 mr-1" /> Input
                                </div>
                                <code className="break-all">{JSON.stringify(event.input).slice(0, 150)}{JSON.stringify(event.input).length > 150 && '...'}</code>
                            </div>
                        )}

                        {event.type === 'tool_end' && event.output && (
                            <div className="p-2 bg-green-50/50 border border-green-100 rounded text-gray-600">
                                <div className="flex items-center text-[10px] text-green-600/70 mb-1">
                                    <CheckCircle2 className="w-3 h-3 mr-1" /> Output
                                </div>
                                <div className="line-clamp-3 text-[10px]">{event.output}</div>
                            </div>
                        )}

                        {event.response && (
                            <div className="p-2 bg-blue-50/50 border border-blue-100 rounded text-blue-800 italic border-l-2 border-l-blue-400">
                                "{event.response.slice(0, 100)}..."
                            </div>
                        )}
                    </div>
                </div>
            ))}
            <div ref={bottomRef} className="h-4" />
        </div>
    );
};
