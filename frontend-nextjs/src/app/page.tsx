"use client";

import { useState, useRef, useEffect } from "react";
import { SendHorizontal } from "lucide-react";
import "./globals.css";
import { Sidebar } from "../components/Sidebar";
import { ChatMessage } from "../components/ChatMessage";

type Role = "user" | "assistant" | "system" | "tool";

interface Message {
  role: Role;
  content: string;
  name?: string;
  tool_calls?: any[];
  tool_call_id?: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
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

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  const visibleMessages = messages.filter(
    (msg) => msg.role !== "system" && msg.role !== "tool" && !(msg.role === "assistant" && msg.tool_calls)
  );

  return (
    <div className="app-layout">
      <Sidebar />
      
      <main className="main-chat">
        <div className="chat-scroll-area">
          {visibleMessages.length === 0 ? (
            <div className="empty-state">
              <h1>How can I help you today?</h1>
              <div className="suggestion-chips">
                <div className="chip" onClick={() => handleSuggestionClick("Where is my order?")}>
                  Where is my order?
                </div>
                <div className="chip" onClick={() => handleSuggestionClick("What is the refund policy?")}>
                  What is the refund policy?
                </div>
                <div className="chip" onClick={() => handleSuggestionClick("I want to refund a final sale item")}>
                  Refund a final sale item
                </div>
              </div>
            </div>
          ) : (
            <div className="messages-wrapper">
              {visibleMessages.map((msg, idx) => (
                <ChatMessage key={idx} role={msg.role} content={msg.content} />
              ))}
              
              {isLoading && (
                <div className="message-row assistant">
                  <div className="avatar ai-avatar">
                    <div className="dot" style={{ background: "white" }}></div>
                  </div>
                  <div className="message-content">
                    <div className="loading-dots">
                      <div className="dot"></div>
                      <div className="dot"></div>
                      <div className="dot"></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div className="input-container-wrapper">
          <form className="glass-input-box glass-panel" onSubmit={handleSubmit}>
            <input
              type="text"
              className="chat-input"
              placeholder="Message AI Support Agent..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <button type="submit" className="send-button" disabled={isLoading || !input.trim()}>
              <SendHorizontal size={18} />
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
