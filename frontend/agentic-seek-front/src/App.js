import React, { useState, useEffect, useRef, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import axios from "axios";
import "./App.css";
import faviconPng from "./logo.png";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "";

function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState("chat");
  const [responseData, setResponseData] = useState(null);
  const [isOnline, setIsOnline] = useState(false);
  const [status, setStatus] = useState("Agent siap");
  const [expandedReasoning, setExpandedReasoning] = useState(new Set());
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const messagesEndRef = useRef(null);

  const fetchLatestAnswer = useCallback(async () => {
    try {
      const res = await axios.get(`${BACKEND_URL}/latest_answer`);
      const data = res.data;
      updateData(data);
      if (!data.answer || data.answer.trim() === "") return;
      const normalizedNewAnswer = normalizeAnswer(data.answer);
      const answerExists = messages.some(
        (msg) => normalizeAnswer(msg.content) === normalizedNewAnswer
      );
      if (!answerExists) {
        setMessages((prev) => [
          ...prev,
          {
            type: "agent",
            content: data.answer,
            reasoning: data.reasoning,
            agentName: data.agent_name,
            status: data.status,
            uid: data.uid,
          },
        ]);
        setStatus(data.status);
        scrollToBottom();
      }
    } catch (error) {
      console.error("Error fetching latest answer:", error);
    }
  }, [messages]);

  useEffect(() => {
    checkHealth();
    const healthInterval = setInterval(checkHealth, 10000);
    return () => clearInterval(healthInterval);
  }, []);

  useEffect(() => {
    const pollInterval = setInterval(() => {
      if (isLoading) {
        fetchLatestAnswer();
        fetchScreenshot();
      }
    }, 5000);
    return () => clearInterval(pollInterval);
  }, [isLoading, fetchLatestAnswer]);

  const checkHealth = async () => {
    try {
      await axios.get(`${BACKEND_URL}/health`);
      setIsOnline(true);
    } catch {
      setIsOnline(false);
    }
  };

  const fetchScreenshot = async () => {
    try {
      const timestamp = new Date().getTime();
      const res = await axios.get(
        `${BACKEND_URL}/screenshots/updated_screen.png?timestamp=${timestamp}`,
        { responseType: "blob" }
      );
      const imageUrl = URL.createObjectURL(res.data);
      setResponseData((prev) => {
        if (prev?.screenshot && prev.screenshot !== "placeholder.png") {
          URL.revokeObjectURL(prev.screenshot);
        }
        return { ...prev, screenshot: imageUrl, screenshotTimestamp: new Date().getTime() };
      });
    } catch (err) {
      setResponseData((prev) => ({
        ...prev,
        screenshot: null,
        screenshotTimestamp: new Date().getTime(),
      }));
    }
  };

  const normalizeAnswer = (answer) => {
    return answer.trim().toLowerCase().replace(/\s+/g, " ").replace(/[.,!?]/g, "");
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const toggleReasoning = (messageIndex) => {
    setExpandedReasoning((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(messageIndex)) newSet.delete(messageIndex);
      else newSet.add(messageIndex);
      return newSet;
    });
  };

  const updateData = (data) => {
    setResponseData((prev) => ({
      ...prev,
      blocks: data.blocks || prev?.blocks || null,
      done: data.done,
      answer: data.answer,
      agent_name: data.agent_name,
      status: data.status,
      uid: data.uid,
    }));
  };

  const handleStop = async (e) => {
    e.preventDefault();
    setIsLoading(false);
    setError(null);
    try {
      await axios.get(`${BACKEND_URL}/stop`);
      setStatus("Menghentikan proses...");
    } catch (err) {
      console.error("Error stopping:", err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    const userQuery = query;
    setMessages((prev) => [...prev, { type: "user", content: userQuery }]);
    setIsLoading(true);
    setError(null);
    setQuery("");
    setActiveView("chat");

    try {
      const res = await axios.post(`${BACKEND_URL}/query`, {
        query: userQuery,
        tts_enabled: false,
      });
      updateData(res.data);
    } catch (err) {
      console.error("Error:", err);
      setError("Gagal memproses pesan.");
      setMessages((prev) => [
        ...prev,
        { type: "error", content: "Error: Tidak bisa mendapatkan respon." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = async () => {
    try {
      await axios.post(`${BACKEND_URL}/new_chat`);
    } catch (err) {
      console.error("Error creating new chat:", err);
    }
    setMessages([]);
    setResponseData(null);
    setError(null);
    setStatus("Agent siap");
    setQuery("");
  };

  const handleClearHistory = async () => {
    try {
      await axios.post(`${BACKEND_URL}/clear_history`);
    } catch (err) {
      console.error("Error clearing history:", err);
    }
    setMessages([]);
    setResponseData(null);
    setError(null);
    setStatus("Riwayat dihapus");
  };

  const navItems = [
    {
      id: "chat",
      label: "Chat",
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
      ),
    },
    {
      id: "editor",
      label: "Editor",
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="16 18 22 12 16 6"/>
          <polyline points="8 6 2 12 8 18"/>
        </svg>
      ),
    },
    {
      id: "browser",
      label: "Browser",
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="2" y1="12" x2="22" y2="12"/>
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
        </svg>
      ),
    },
  ];

  return (
    <div className="app-container">
      <aside className={`sidebar ${sidebarCollapsed ? "collapsed" : ""}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <img src={faviconPng} alt="Agent Dzeck AI" className="sidebar-logo-img" />
            {!sidebarCollapsed && <span className="sidebar-title">Agent Dzeck AI</span>}
          </div>
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            title={sidebarCollapsed ? "Perluas" : "Kecilkan"}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              {sidebarCollapsed ? (
                <polyline points="9 18 15 12 9 6"/>
              ) : (
                <polyline points="15 18 9 12 15 6"/>
              )}
            </svg>
          </button>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${activeView === item.id ? "active" : ""}`}
              onClick={() => { setActiveView(item.id); setMobileMenuOpen(false); }}
              title={item.label}
            >
              <span className="nav-icon">{item.icon}</span>
              {!sidebarCollapsed && <span className="nav-label">{item.label}</span>}
            </button>
          ))}
        </nav>

        <div className="sidebar-actions">
          <button className="sidebar-action-btn new-chat-btn" onClick={handleNewChat} title="Chat Baru">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            {!sidebarCollapsed && <span>Chat Baru</span>}
          </button>
          <button className="sidebar-action-btn clear-btn" onClick={handleClearHistory} title="Hapus Riwayat">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            {!sidebarCollapsed && <span>Hapus Riwayat</span>}
          </button>
        </div>

        <div className="sidebar-footer">
          <div className={`status-badge ${isOnline ? "online" : "offline"}`}>
            <div className="status-dot-small" />
            {!sidebarCollapsed && (
              <span>{isOnline ? "Online" : "Offline"}</span>
            )}
          </div>
        </div>
      </aside>

      <div className="mobile-header">
        <button className="mobile-menu-btn" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
        <div className="mobile-brand">
          <img src={faviconPng} alt="Agent Dzeck AI" className="mobile-logo" />
          <span>Agent Dzeck AI</span>
        </div>
        <div className={`status-badge small ${isOnline ? "online" : "offline"}`}>
          <div className="status-dot-small" />
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="mobile-overlay" onClick={() => setMobileMenuOpen(false)}>
          <div className="mobile-drawer" onClick={(e) => e.stopPropagation()}>
            <nav className="mobile-nav">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  className={`mobile-nav-item ${activeView === item.id ? "active" : ""}`}
                  onClick={() => { setActiveView(item.id); setMobileMenuOpen(false); }}
                >
                  <span className="nav-icon">{item.icon}</span>
                  <span>{item.label}</span>
                </button>
              ))}
              <hr className="mobile-divider" />
              <button className="mobile-nav-item" onClick={() => { handleNewChat(); setMobileMenuOpen(false); }}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                <span>Chat Baru</span>
              </button>
              <button className="mobile-nav-item danger" onClick={() => { handleClearHistory(); setMobileMenuOpen(false); }}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                <span>Hapus Riwayat</span>
              </button>
            </nav>
          </div>
        </div>
      )}

      <main className="main-content">
        {activeView === "chat" && (
          <div className="chat-panel">
            <div className="panel-header">
              <h2>Chat AI Agent</h2>
              <span className="panel-badge">{status}</span>
            </div>
            <div className="messages-container">
              {messages.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                    </svg>
                  </div>
                  <h3>Selamat Datang di Agent Dzeck AI</h3>
                  <p>AI Agent full-stack siap membantu Anda. Ketik pesan di bawah untuk mulai!</p>
                </div>
              ) : (
                messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`message ${msg.type === "user" ? "user-msg" : msg.type === "agent" ? "agent-msg" : "error-msg"}`}
                  >
                    {msg.type === "agent" && (
                      <div className="msg-meta">
                        <span className="agent-badge">{msg.agentName}</span>
                        {msg.reasoning && (
                          <button className="reasoning-btn" onClick={() => toggleReasoning(index)}>
                            {expandedReasoning.has(index) ? "Sembunyikan" : "Lihat"} Alasan
                          </button>
                        )}
                      </div>
                    )}
                    {msg.type === "agent" && msg.reasoning && expandedReasoning.has(index) && (
                      <div className="reasoning-box">
                        <ReactMarkdown>{msg.reasoning}</ReactMarkdown>
                      </div>
                    )}
                    <div className="msg-body">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  </div>
                ))
              )}
              {isLoading && (
                <div className="typing-indicator">
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            <form onSubmit={handleSubmit} className="chat-input-form">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ketik pesan Anda di sini..."
                disabled={isLoading}
              />
              <div className="chat-input-actions">
                <button type="submit" disabled={isLoading || !query.trim()} className="send-btn" title="Kirim">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </button>
                {isLoading && (
                  <button type="button" onClick={handleStop} className="stop-btn" title="Hentikan">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                      <rect x="6" y="6" width="12" height="12" fill="currentColor" rx="2"/>
                    </svg>
                  </button>
                )}
              </div>
            </form>
          </div>
        )}

        {activeView === "editor" && (
          <div className="editor-panel">
            <div className="panel-header">
              <h2>Editor - Output Kode</h2>
              <span className="panel-badge">
                {responseData?.blocks ? `${Object.keys(responseData.blocks).length} blok` : "Kosong"}
              </span>
            </div>
            <div className="editor-content">
              {responseData && responseData.blocks && Object.values(responseData.blocks).length > 0 ? (
                Object.values(responseData.blocks).map((block, index) => (
                  <div key={index} className="code-block">
                    <div className="code-block-header">
                      <span className="code-block-tool">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
                        {block.tool_type}
                      </span>
                      <span className={`code-block-status ${block.success ? "success" : "failure"}`}>
                        {block.success ? "Berhasil" : "Gagal"}
                      </span>
                    </div>
                    <pre className="code-block-content">{block.block}</pre>
                    {block.feedback && (
                      <div className="code-block-feedback">
                        <span>Feedback:</span> {block.feedback}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <polyline points="16 18 22 12 16 6"/>
                      <polyline points="8 6 2 12 8 18"/>
                    </svg>
                  </div>
                  <h3>Editor View</h3>
                  <p>Di sini akan muncul output kode, hasil eksekusi tool, dan log dari AI agent saat memproses permintaan Anda.</p>
                  <p className="empty-hint">Kirim pesan ke AI untuk melihat hasilnya di sini.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeView === "browser" && (
          <div className="browser-panel">
            <div className="panel-header">
              <h2>Browser View</h2>
              <button className="refresh-btn" onClick={fetchScreenshot} title="Refresh">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="23 4 23 10 17 10"/>
                  <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
                </svg>
              </button>
            </div>
            <div className="browser-content">
              {responseData?.screenshot ? (
                <div className="browser-frame">
                  <div className="browser-toolbar">
                    <div className="browser-dots">
                      <span className="dot red" />
                      <span className="dot yellow" />
                      <span className="dot green" />
                    </div>
                    <div className="browser-url-bar">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/></svg>
                      <span>agent-browser://preview</span>
                    </div>
                  </div>
                  <img
                    src={responseData.screenshot}
                    alt="Browser Screenshot"
                    className="browser-screenshot"
                    key={responseData.screenshotTimestamp || "default"}
                  />
                </div>
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <circle cx="12" cy="12" r="10"/>
                      <line x1="2" y1="12" x2="22" y2="12"/>
                      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                    </svg>
                  </div>
                  <h3>Browser Preview</h3>
                  <p>Tampilan browser akan muncul di sini saat AI agent membuka halaman web.</p>
                  <p className="empty-hint">Minta AI untuk membuka website untuk melihat preview-nya.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      <div className="mobile-bottom-nav">
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`bottom-nav-item ${activeView === item.id ? "active" : ""}`}
            onClick={() => setActiveView(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="bottom-nav-label">{item.label}</span>
          </button>
        ))}
      </div>

      {error && (
        <div className="toast-error">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
          <span>{error}</span>
          <button onClick={() => setError(null)}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
