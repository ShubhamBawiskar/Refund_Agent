import { MessageSquarePlus, Settings, User } from "lucide-react";

export function Sidebar() {
  return (
    <div className="sidebar">
      <button className="new-chat-btn">
        <MessageSquarePlus size={18} />
        New Chat
      </button>
      
      <div className="chat-history">
        <div className="history-item">Recent Refund Query</div>
        <div className="history-item">Where is my order?</div>
        <div className="history-item">Final Sale Policy</div>
      </div>
      
      <div style={{ marginTop: 'auto', display: 'flex', gap: '1rem', color: 'var(--text-secondary)' }}>
        <User size={20} style={{ cursor: 'pointer' }} />
        <Settings size={20} style={{ cursor: 'pointer' }} />
      </div>
    </div>
  );
}
