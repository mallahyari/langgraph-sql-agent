import React from 'react';
import type { AgentEvent } from '../types';
import { CheckCircle2, Loader2, Database, Brain, Terminal, FileText, PieChart, Bot, Sparkles } from 'lucide-react';
import { cn } from '../lib/utils';
import { VisualizationRenderer } from './VisualizationRenderer';

interface ThinkingProcessProps {
    events: AgentEvent[];
    isComplete: boolean;
}

export const ThinkingProcess: React.FC<ThinkingProcessProps> = ({ events, isComplete }) => {

    const getNodeInfo = (nodeName: string) => {
        switch (nodeName) {
            case 'query_router': return { label: 'Analyzing Intent', icon: Brain, color: 'text-purple-500', bg: 'bg-purple-100' };
            case 'query_rewriter': return { label: 'Refining Query', icon: Sparkles, color: 'text-amber-500', bg: 'bg-amber-100' };
            case 'table_selector': return { label: 'Selecting Tables', icon: Database, color: 'text-blue-500', bg: 'bg-blue-100' };
            case 'sql_generator': return { label: 'Generating SQL', icon: Terminal, color: 'text-slate-600', bg: 'bg-slate-100' };
            case 'sql_validator': return { label: 'Validating SQL', icon: CheckCircle2, color: 'text-green-500', bg: 'bg-green-100' };
            case 'sql_executor': return { label: 'Executing Query', icon: Database, color: 'text-emerald-600', bg: 'bg-emerald-100' };
            case 'response_synthesizer': return { label: 'Synthesizing Answer', icon: FileText, color: 'text-indigo-500', bg: 'bg-indigo-100' };
            case 'visualization_planner': return { label: 'Planning Visuals', icon: PieChart, color: 'text-pink-500', bg: 'bg-pink-100' };
            case 'visualization_generator': return { label: 'Creating Chart', icon: PieChart, color: 'text-pink-600', bg: 'bg-pink-100' };
            case 'general_agent': return { label: 'Answering', icon: Bot, color: 'text-blue-600', bg: 'bg-blue-100' };
            default: return { label: 'Processing', icon: Loader2, color: 'text-gray-500', bg: 'bg-gray-100' };
        }
    };

    // Group events by node to avoid duplicates and show content
    // We only want to show distinct steps
    const steps = events.reduce((acc, event) => {
        if (event.type === 'node_update' && event.node) {
            // Find if we already have this node in the sequence
            const existingIndex = acc.findIndex(s => s.node === event.node);

            if (existingIndex !== -1) {
                // Update existing step with new data if available (e.g. SQL or Viz)
                // We merge so we don't lose previous info
                acc[existingIndex].event = { ...acc[existingIndex].event, ...event };
            } else {
                // Add new step
                acc.push({ node: event.node, event });
            }
        }
        return acc;
    }, [] as { node: string, event: AgentEvent }[]);

    if (steps.length === 0) return null;

    return (
        <div className="w-full max-w-2xl my-6">
            <div className="flex items-center space-x-2 mb-4 px-1">
                <div className="h-4 w-1 bg-gradient-to-b from-blue-500 to-indigo-600 rounded-full"></div>
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Thinking Process</span>
            </div>

            <div className="relative pl-4 space-y-0 ml-2">
                {/* Vertical Line */}
                <div
                    className="absolute left-[3px] top-2 bottom-0 w-0.5 bg-gray-100"
                    style={{ height: 'calc(100% - 20px)' }}
                />

                {steps.map((step, idx) => {
                    const { label, icon: Icon, color, bg } = getNodeInfo(step.node);
                    const isLast = idx === steps.length - 1;
                    const isActive = isLast && !isComplete;

                    return (
                        <div key={idx} className={cn(
                            "relative pl-8 pb-8 transition-all duration-500 ease-in-out group",
                            isActive ? "opacity-100 scale-100" : "opacity-70 scale-95"
                        )}>
                            {/* Dot on timeline */}
                            <div className={cn(
                                "absolute -left-1.5 top-0 w-4 h-4 rounded-full border-2 bg-white flex items-center justify-center transition-all duration-300 z-10",
                                isActive
                                    ? "border-blue-500 shadow-[0_0_0_4px_rgba(59,130,246,0.1)] scale-110"
                                    : "border-gray-300 group-hover:border-gray-400"
                            )}>
                                {isActive && <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />}
                            </div>

                            <div className="flex flex-col space-y-3">
                                <div className="flex items-center space-x-3">
                                    <div className={cn("p-1.5 rounded-md transition-colors duration-300", bg)}>
                                        <Icon className={cn("w-4 h-4", color, isActive && "animate-pulse")} />
                                    </div>
                                    <span className={cn("text-sm font-medium transition-colors duration-300", isActive ? "text-gray-900" : "text-gray-500")}>
                                        {label}
                                    </span>
                                </div>

                                {/* Content: SQL */}
                                {step.event.sql && (
                                    <div className="mt-2 bg-slate-900 rounded-xl p-4 overflow-x-auto border border-slate-700 shadow-lg animate-in fade-in slide-in-from-left-4 duration-500 relative group/code">
                                        <div className="absolute top-2 right-2 flex space-x-1 opacity-0 group-hover/code:opacity-100 transition-opacity">
                                            <div className="flex space-x-1">
                                                <div className="w-2.5 h-2.5 rounded-full bg-red-500/20"></div>
                                                <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/20"></div>
                                                <div className="w-2.5 h-2.5 rounded-full bg-green-500/20"></div>
                                            </div>
                                        </div>
                                        <div className="flex items-center text-xs text-slate-500 mb-2 font-mono tracking-wide">
                                            <Terminal className="w-3 h-3 mr-1.5" /> SQL GENERATED
                                        </div>
                                        <code className="text-sm font-mono text-blue-300 whitespace-pre-wrap leading-relaxed">
                                            {step.event.sql}
                                        </code>
                                    </div>
                                )}

                                {/* Content: Visualization */}
                                {step.event.visualization && (
                                    <div className="mt-2 w-full animate-in zoom-in-95 duration-700 ease-out">
                                        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-1">
                                            <VisualizationRenderer spec={step.event.visualization} />
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
