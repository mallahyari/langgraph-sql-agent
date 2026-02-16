import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import { ThinkingProcess } from './ThinkingProcess';
import { Send, Bot, Database, Sparkles, User, RefreshCw } from 'lucide-react';
import { cn } from '../lib/utils';

export const ChatInterface: React.FC = () => {
    const { messages, isLoading, sendMessage, currentTrace } = useChat();
    const [input, setInput] = useState('');
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, currentTrace]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (input.trim() && !isLoading) {
            sendMessage(input);
            setInput('');
        }
    };

    return (
        <div className="flex h-screen bg-white font-sans text-slate-900 selection:bg-blue-100 selection:text-blue-900">
            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col h-full relative max-w-5xl mx-auto w-full shadow-2xl shadow-slate-200/50 bg-white border-x border-slate-50">
                {/* Header */}
                <header className="h-16 bg-white/80 backdrop-blur-md border-b border-slate-100 flex items-center justify-between px-8 sticky top-0 z-20">
                    <div className="flex items-center space-x-3 group cursor-pointer">
                        <div className="relative">
                            <div className="absolute inset-0 bg-blue-500 blur-lg opacity-20 group-hover:opacity-40 transition-opacity rounded-full"></div>
                            <div className="p-2 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-xl shadow-lg relative z-10 group-hover:scale-105 transition-transform">
                                <Database className="w-5 h-5 text-white" />
                            </div>
                        </div>
                        <div>
                            <h1 className="text-lg font-bold text-slate-900 leading-tight tracking-tight">Distribution Analytics</h1>
                            <p className="text-xs text-slate-500 font-medium flex items-center">
                                <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5 animate-pulse"></span>
                                Agent Active
                            </p>
                        </div>
                    </div>
                </header>

                {/* Messages List */}
                <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-10 scroll-smooth custom-scrollbar">
                    {messages.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-center p-8 animate-in fade-in zoom-in-95 duration-700">
                            <div className="w-24 h-24 bg-gradient-to-tr from-blue-50 to-indigo-50 rounded-3xl flex items-center justify-center mb-8 shadow-inner ring-1 ring-slate-100 overflow-hidden relative">
                                <div className="absolute inset-0 bg-grid-slate-200/50 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))]"></div>
                                <Sparkles className="w-10 h-10 text-blue-600 relative z-10" />
                            </div>
                            <h2 className="text-3xl font-bold text-slate-800 mb-3 tracking-tight">How can I help you today?</h2>
                            <p className="text-slate-500 max-w-md text-lg leading-relaxed mb-10">
                                I can analyze the Chinook database to answer questions about sales, customers, and tracks.
                            </p>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl w-full">
                                {[
                                    { t: "Global Sales", q: "Show total sales revenue by country" },
                                    { t: "Top Customers", q: "Who are the top 5 customers by purchase amount?" },
                                    { t: "Genre Trends", q: "Which genres are most popular in the USA?" },
                                    { t: "Invoice Analysis", q: "Show the number of invoices per year" }
                                ].map((item) => (
                                    <button
                                        key={item.q}
                                        onClick={() => sendMessage(item.q)}
                                        className="group p-4 bg-white border border-slate-200 rounded-2xl text-left hover:border-blue-400 hover:shadow-lg hover:shadow-blue-500/5 transition-all duration-300 relative overflow-hidden"
                                    >
                                        <div className="absolute inset-0 bg-blue-50 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                                        <div className="relative z-10">
                                            <div className="text-xs font-semibold text-blue-600 mb-1 uppercase tracking-wider">{item.t}</div>
                                            <div className="text-slate-700 text-sm font-medium">{item.q}</div>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {messages.map((msg, idx) => {
                        const isLastMessage = idx === messages.length - 1;

                        return (
                            <div key={idx} className={cn(
                                "group flex w-full max-w-3xl mx-auto space-x-6",
                                msg.role === 'user' ? "justify-end" : "justify-start"
                            )}>
                                {msg.role === 'assistant' && (
                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-indigo-500/20 mt-1 ring-2 ring-white z-10">
                                        <Bot className="w-6 h-6 text-white" />
                                    </div>
                                )}

                                <div className={cn(
                                    "flex flex-col max-w-[95%]",
                                    msg.role === 'user' ? "items-end" : "items-start"
                                )}>
                                    {/* Thinking Process Integration */}
                                    {msg.role === 'assistant' && (
                                        <ThinkingProcess
                                            events={isLastMessage ? currentTrace : (msg.trace || [])}
                                            isComplete={!isLoading || !isLastMessage}
                                        />
                                    )}

                                    {/* Message Bubble */}
                                    {msg.content && (
                                        <div className={cn(
                                            "p-6 shadow-sm relative text-[15px] leading-7 tracking-wide",
                                            msg.role === 'user'
                                                ? "bg-slate-900 text-white rounded-3xl rounded-tr-md shadow-xl shadow-slate-900/10"
                                                : "bg-white border border-slate-100 text-slate-800 rounded-3xl rounded-tl-md shadow-xl shadow-slate-200/40"
                                        )}>
                                            <div className="prose prose-slate max-w-none dark:prose-invert break-words whitespace-pre-wrap">
                                                {msg.content}
                                            </div>
                                        </div>
                                    )}

                                </div>

                                {msg.role === 'user' && (
                                    <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center flex-shrink-0 mt-1 ring-2 ring-white">
                                        <User className="w-6 h-6 text-slate-500" />
                                    </div>
                                )}
                            </div>
                        );
                    })}
                    <div ref={bottomRef} className="h-4" />
                </div>

                {/* Input Area */}
                <div className="p-6 bg-white/80 backdrop-blur-lg border-t border-slate-100 flex justify-center">
                    <form onSubmit={handleSubmit} className="max-w-3xl w-full relative flex items-center transition-all">
                        <div className="absolute inset-0 bg-gradient-to-r from-blue-100 to-indigo-100 rounded-2xl blur-xl opacity-20 pointer-events-none"></div>
                        <div className="relative w-full flex items-center bg-white rounded-2xl border border-slate-200 shadow-xl shadow-slate-200/20 focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-400 transition-all overflow-hidden">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Ask a question about your data..."
                                className="flex-1 py-4 px-6 bg-transparent border-none focus:ring-0 text-slate-900 placeholder:text-slate-400 text-base"
                                disabled={isLoading}
                            />
                            <div className="pr-2 flex items-center">
                                {isLoading ? (
                                    <div className="p-3 mr-1">
                                        <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />
                                    </div>
                                ) : (
                                    <button
                                        type="submit"
                                        disabled={!input.trim()}
                                        className="p-3 mr-1 bg-gradient-to-tr from-blue-600 to-indigo-600 text-white rounded-xl hover:shadow-lg hover:shadow-blue-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95 duration-200"
                                    >
                                        <Send className="w-5 h-5" />
                                    </button>
                                )}
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

