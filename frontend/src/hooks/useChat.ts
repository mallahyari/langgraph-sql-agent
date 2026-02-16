import { useState } from 'react';
import type { Message, AgentEvent } from '../types';

export const useChat = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [currentTrace, setCurrentTrace] = useState<AgentEvent[]>([]);

    const sendMessage = async (content: string) => {
        setIsLoading(true);
        setCurrentTrace([]); // Clear trace for new message

        // Add user message immediately
        const userMsg: Message = { role: 'user', content };
        setMessages(prev => [...prev, userMsg]);

        try {
            const response = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: content })
            });

            if (!response.ok) throw new Error('Network response was not ok');
            if (!response.body) throw new Error('No response body');

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let assistantMessage: Message = {
                role: 'assistant',
                content: '',
                trace: []
            };

            // We'll update this reference to update the UI progressively
            setMessages(prev => [...prev, assistantMessage]);

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const jsonStr = line.replace('data: ', '');
                            const event: AgentEvent = JSON.parse(jsonStr);

                            // Update trace
                            setCurrentTrace(prev => [...prev, event]);

                            // Handle specific event types for message content
                            if (event.type === 'token' && event.content) {
                                assistantMessage.content += event.content;
                            }

                            if (event.response) {
                                // Optional: Ensure content matches final response
                                assistantMessage.content = event.response;
                            }

                            if (event.visualization) {
                                assistantMessage.visualization = event.visualization;
                            }

                            if (event.sql) {
                                assistantMessage.sql = event.sql;
                            }

                            // Update the last message in state
                            setMessages(prev => {
                                const newMessages = [...prev];
                                newMessages[newMessages.length - 1] = {
                                    ...assistantMessage,
                                    trace: [...(assistantMessage.trace || []), event] // Keep trace in message too if needed
                                };
                                return newMessages;
                            });

                        } catch (e) {
                            console.error('Error parsing SSE:', e);
                        }
                    }
                }
            }

        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    return { messages, isLoading, sendMessage, currentTrace };
};
