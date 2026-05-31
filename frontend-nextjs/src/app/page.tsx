"use client";

import { useState, useRef, useEffect } from "react";
import "./globals.css";

type Role = "user" | "assistant" | "system" | "tool";

interface Message {
  role: Role;
  content: string;
  name?: string;
  tool_calls?: any[];
  tool_call_id?: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! I am the AI Support Agent. How can I help you with your refund today? Please provide your email and order ID if you have them.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: Message = { role: "user", content: input };
    const newMessages = [...messages, userMsg];
    
    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: newMessages }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch from backend");
      }

      const data = await response.json();
      
      if (data.messages && data.messages.length > 0) {
        setMessages(data.messages);
      } else {
        setMessages([
          ...newMessages,
          { role: "assistant", content: data.final_message },
        ]);
      }
    } catch (error) {
      console.error(error);
      setMessages([
        ...newMessages,
        { role: "assistant", content: "Sorry, I am having trouble connecting to the server." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>Premium Customer Support</h1>
      </div>
      
      <div className="chat-messages">
        {messages.map((msg, idx) => {
          // Skip system, tool, and tool_calls messages for the UI
          if (
            msg.role === "system" ||
            msg.role === "tool" ||
            (msg.role === "assistant" && msg.tool_calls)
          ) {
            return null;
          }

          return (
            <div key={idx} className={`message ${msg.role}`}>
              {msg.content}
            </div>
          );
        })}
        
        {isLoading && (
          <div className="message assistant">
            <div className="loading-dots">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-container" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          placeholder="Type your message here..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
        <button type="submit" className="send-button" disabled={isLoading || !input.trim()}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </form>
    </div>
  );
}
