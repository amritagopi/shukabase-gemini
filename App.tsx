import React, { useState, useEffect, useRef } from 'react';
import { Send, Settings, BookOpen, Database, AlertCircle, Menu, X, Search, Sparkles, Server, Scroll } from 'lucide-react';
import { Message, SourceChunk, AppSettings, Conversation, ConversationHeader } from './types';
import { generateRAGResponse, getConversations, getConversation, saveConversation } from './services/geminiService';
import { DEMO_CHUNKS } from './constants';
import { ParsedContent } from './utils/citationParser';
import ConversationHistory from './ConversationHistory';

const DEFAULT_SETTINGS: AppSettings = {
  apiKey: process.env.API_KEY || '',
  backendUrl: 'http://localhost:5000/api/search',
  useMockData: false,
  model: 'gemini-2.5-flash-lite',
};

const App: React.FC = () => {
  const [conversations, setConversations] = useState<ConversationHeader[]>([]);
  const [activeConversation, setActiveConversation] = useState<Conversation | null>(null);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [currentSources, setCurrentSources] = useState<SourceChunk[]>([]);
  const [highlightedSourceId, setHighlightedSourceId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loadConversations = async () => {
      try {
        const convos = await getConversations();
        setConversations(convos);
      } catch (error) {
        console.error("Failed to load conversations", error);
      }
    };
    loadConversations();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeConversation?.messages]);

  const retrieveRelevantChunks = async (query: string): Promise<SourceChunk[]> => {
    if (settings.useMockData) {
      await new Promise(resolve => setTimeout(resolve, 600));
      return DEMO_CHUNKS.map(chunk => ({
        ...chunk,
        score: 0.8 + Math.random() * 0.1
      })).slice(0, 4);
    } else {
      if (!settings.backendUrl) throw new Error("Backend URL missing");
      try {
        const isCyrillic = /[а-яА-ЯёЁ]/.test(query);
        const lang = isCyrillic ? 'ru' : 'en';
        const response = await fetch(settings.backendUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: query, language: lang })
        });
        if (!response.ok) throw new Error(`Backend Error: ${response.status}`);
        const data = await response.json();
        if (!data.success) throw new Error(data.error || "Unknown error from backend");
        return (data.results || []).map((item: any) => ({
          id: `${(item.book || 'unknown').replace(/\s+/g, "").toLowerCase()}.${item.chapter}.${item.verse}`,
          bookTitle: item.book || 'Unknown',
          chapter: item.chapter,
          verse: item.verse,
          content: item.text,
          score: item.final_score || item.score || 0
        }));
      } catch (err: any) {
        console.error("Retrieval error", err);
        throw new Error(`Connection Failed: ${err.message}. \n\nMake sure 'rag/rag_api_server.py' is running on port 5000.`);
      }
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    if (!settings.apiKey) {
      setIsSettingsOpen(true);
      return;
    }

    const userMsgContent = input;
    setInput('');
    setLoading(true);

    const userMessage: Message = { role: 'user', parts: [{ text: userMsgContent }] };
    const thinkingMessage: Message = { role: 'model', parts: [{ text: '' }], isThinking: true };

    let conversationToUpdate: Conversation;
    if (activeConversation) {
      conversationToUpdate = { ...activeConversation, messages: [...activeConversation.messages, userMessage, thinkingMessage] };
    } else {
      const newId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      conversationToUpdate = {
        id: newId,
        title: userMsgContent.substring(0, 50),
        createdAt: new Date().toISOString(),
        messages: [userMessage, thinkingMessage],
      };
    }
    
    setActiveConversation(conversationToUpdate);

    try {
      const chunks = await retrieveRelevantChunks(userMsgContent);
      setCurrentSources(chunks);

      let responseText: string;
      if (chunks.length === 0) {
        responseText = "I searched the scriptures but found no relevant verses matching your query.";
      } else {
        const history = conversationToUpdate.messages
          .filter(m => !m.isThinking)
          .slice(-50) // Short-term memory: last 50 messages
          .map(m => ({ role: m.role, parts: m.parts }));
        
        responseText = await generateRAGResponse(userMsgContent, chunks, settings, history);
      }

      const finalBotMessage: Message = {
        role: 'model',
        parts: [{ text: responseText }],
        relatedChunkIds: chunks.map(c => c.id),
      };

      // Replace the "thinking" message with the final response
      const finalMessages = conversationToUpdate.messages.slice(0, -1).concat(finalBotMessage);
      const finalConversation = { ...conversationToUpdate, messages: finalMessages };
      
      setActiveConversation(finalConversation);
      await saveConversation(finalConversation);
      
      // Update conversations list if it's a new chat
      if (!conversations.some(c => c.id === finalConversation.id)) {
        setConversations(prev => [{ id: finalConversation.id, title: finalConversation.title, createdAt: finalConversation.createdAt }, ...prev]);
      }

    } catch (error: any) {
      const errorMessage: Message = {
        role: 'model',
        parts: [{ text: `❌ **Error**: ${error.message}` }],
      };
      const finalMessages = conversationToUpdate.messages.slice(0, -1).concat(errorMessage);
      const finalConversation = { ...conversationToUpdate, messages: finalMessages };
      setActiveConversation(finalConversation);
      await saveConversation(finalConversation);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSelectConversation = async (id: string) => {
    try {
      const convo = await getConversation(id);
      setActiveConversation(convo);
    } catch (error) {
      console.error("Failed to load conversation", error);
    }
  };
  
  const handleNewChat = () => {
    setActiveConversation(null);
    setCurrentSources([]);
  };

  const handleCitationClick = (id: string) => {
    setHighlightedSourceId(id);
    if (!sidebarOpen) setSidebarOpen(true);
    setTimeout(() => {
      const el = document.getElementById(`source-${id}`);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.classList.add('ring-2', 'ring-amber-500');
        setTimeout(() => el.classList.remove('ring-2', 'ring-amber-500'), 2000);
      }
    }, 100);
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 overflow-hidden font-sans">
      
      {/* LEFT PANEL: Conversation History */}
      <ConversationHistory 
        conversations={conversations}
        activeConversationId={activeConversation?.id || null}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
      />

      {/* MIDDLE PANEL: Chat Interface */}
      <div className="flex-1 flex flex-col h-full min-w-0">
        <header className="h-16 border-b border-slate-800 flex items-center justify-between px-6 bg-slate-950">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-600 to-orange-700 flex items-center justify-center shadow-lg shadow-orange-900/50">
              <Scroll className="text-white" size={18} />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-tight text-slate-100">Shukabase AI</h1>
              <p className="text-xs text-slate-500">Gemini Intelligence + Local RAG</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className={`hidden md:flex items-center gap-1.5 text-[10px] uppercase font-bold tracking-wider px-2 py-1 rounded border ${settings.useMockData ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'}`}>
              {settings.useMockData ? 'Demo Mode' : 'Connected'}
            </div>
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="p-2 text-slate-400 hover:text-white transition-colors hover:bg-slate-800 rounded-lg"
            >
              <Settings size={20} />
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
          {(activeConversation?.messages || []).map((msg, index) => (
            !msg.isThinking ? (
              <div
                key={`${activeConversation?.id}-${index}`}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[95%] md:max-w-[80%] rounded-2xl px-5 py-4 shadow-xl ${msg.role === 'user'
                      ? 'bg-gradient-to-r from-amber-700 to-orange-800 text-white rounded-tr-none'
                      : 'bg-slate-800 border border-slate-700 text-slate-200 rounded-tl-none'
                  }`}
                >
                  {msg.role === 'user' ? (
                    <p className="whitespace-pre-wrap">{msg.parts[0].text}</p>
                  ) : (
                    <ParsedContent content={msg.parts[0].text} onCitationClick={handleCitationClick} />
                  )}
                  <div className="mt-2 flex items-center justify-between opacity-50 text-[10px] uppercase tracking-wider">
                    <span>{new Date(msg.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    {msg.role === 'model' && (
                      <span className="flex items-center gap-1"><Sparkles size={10} />Gemini 2.5</span>
                    )}
                  </div>
                </div>
              </div>
            ) : null
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-none px-5 py-4 flex items-center gap-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-amber-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                  <div className="w-2 h-2 bg-amber-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                  <div className="w-2 h-2 bg-amber-500 rounded-full animate-bounce"></div>
                </div>
                <span className="text-xs text-slate-400 font-medium">Consulting scriptures...</span>
              </div>
            </div>
          )}
          {!activeConversation && (
             <div className="flex flex-col items-center justify-center h-full text-slate-500">
                <Sparkles size={48} className="mb-4" />
                <h2 className="text-2xl font-bold mb-2">Shukabase AI</h2>
                <p>Select a conversation or start a new chat.</p>
              </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 border-t border-slate-800 bg-slate-900/80 backdrop-blur-sm">
          <div className="max-w-4xl mx-auto relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask a question about the scriptures..."
              className="w-full bg-slate-800 border border-slate-700 text-slate-100 placeholder-slate-500 rounded-xl pl-4 pr-12 py-3.5 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 transition-all shadow-lg"
              disabled={loading}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="absolute right-2 top-2 p-1.5 bg-amber-600 text-white rounded-lg hover:bg-amber-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* RIGHT PANEL: Sources Sidebar */}
      <div
        className={`fixed inset-y-0 right-0 z-40 w-full sm:w-96 bg-slate-950 border-l border-slate-800 shadow-2xl transform transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0 lg:w-96 ${sidebarOpen ? 'translate-x-0' : 'translate-x-full'}`}
      >
        <div className="h-full flex flex-col">
          <div className="h-16 flex items-center justify-between px-6 border-b border-slate-800 bg-slate-950">
            <h2 className="font-semibold text-slate-200 flex items-center gap-2">
              <Database size={18} className="text-amber-500" />
              Retrieved Verses
            </h2>
            <div className="text-xs font-mono text-slate-500 bg-slate-900 px-2 py-1 rounded">
              {currentSources.length} found
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {currentSources.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-600 p-8 text-center">
                <BookOpen size={48} className="mb-4 opacity-20" />
                <p className="text-sm">No verses loaded.</p>
                <p className="text-xs mt-2 opacity-50">Your search results will appear here.</p>
              </div>
            ) : (
              currentSources.map((chunk) => (
                <div
                  key={chunk.id}
                  id={`source-${chunk.id}`}
                  className={`
                    p-4 rounded-xl border transition-all duration-300 cursor-pointer group
                    ${highlightedSourceId === chunk.id
                      ? 'bg-amber-900/20 border-amber-500 shadow-[0_0_15px_rgba(245,158,11,0.15)]'
                      : 'bg-slate-900 border-slate-800 hover:border-slate-700'
                    }
                  `}
                  onClick={() => setHighlightedSourceId(chunk.id)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-amber-500 bg-amber-950/30 px-2 py-0.5 rounded border border-amber-500/20 truncate max-w-[180px]">
                      {chunk.bookTitle}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono group-hover:text-slate-400">
                      {Math.round(chunk.score * 100)}%
                    </span>
                  </div>

                  <h4 className="text-xs font-semibold text-slate-300 mb-2 font-mono flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-600"></span>
                    {chunk.chapter && chunk.verse
                      ? `Chapter ${chunk.chapter}, Verse ${chunk.verse}`
                      : `Page ${chunk.pageNumber}`}
                  </h4>

                  <p className="text-sm text-slate-400 leading-relaxed font-serif border-l-2 border-slate-700 pl-3 line-clamp-6 group-hover:line-clamp-none transition-all">
                    "{chunk.content}"
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Settings Modal */}
      {isSettingsOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md shadow-2xl">
            <div className="p-6 border-b border-slate-800 flex justify-between items-center">
              <h3 className="font-bold text-lg text-slate-100">Settings</h3>
              <button onClick={() => setIsSettingsOpen(false)} className="text-slate-400 hover:text-white">
                <X size={20} />
              </button>
            </div>

            <div className="p-6 space-y-6">

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Gemini API Key</label>
                <input
                  type="password"
                  value={settings.apiKey}
                  onChange={(e) => setSettings({ ...settings, apiKey: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:ring-1 focus:ring-amber-500 focus:outline-none"
                />
              </div>

              <div className="space-y-4">
                <label className="text-sm font-medium text-slate-300">Data Connection</label>
                <div className="flex gap-4">
                  <label className={`
                    flex-1 flex flex-col items-center gap-2 p-4 rounded-xl border cursor-pointer transition-all
                    ${settings.useMockData
                      ? 'bg-amber-900/20 border-amber-500 text-amber-200'
                      : 'bg-slate-950 border-slate-800 text-slate-500 hover:border-slate-700'
                    }
                  `}>
                    <input type="radio" className="hidden" checked={settings.useMockData} onChange={() => setSettings({ ...settings, useMockData: true })} />
                    <BookOpen size={24} />
                    <span className="text-xs font-semibold">Demo</span>
                  </label>

                  <label className={`
                    flex-1 flex flex-col items-center gap-2 p-4 rounded-xl border cursor-pointer transition-all
                    ${!settings.useMockData
                      ? 'bg-amber-900/20 border-amber-500 text-amber-200'
                      : 'bg-slate-950 border-slate-800 text-slate-500 hover:border-slate-700'
                    }
                  `}>
                    <input type="radio" className="hidden" checked={!settings.useMockData} onChange={() => setSettings({ ...settings, useMockData: false })} />
                    <Server size={24} />
                    <span className="text-xs font-semibold">Bridge</span>
                  </label>
                </div>
              </div>

              {!settings.useMockData && (
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">Backend URL</label>
                  <input
                    type="text"
                    value={settings.backendUrl}
                    onChange={(e) => setSettings({ ...settings, backendUrl: e.target.value })}
                    placeholder="http://localhost:8000/search"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:ring-1 focus:ring-amber-500 focus:outline-none"
                  />
                  <div className="flex items-start gap-2 text-xs text-amber-500/80 bg-amber-950/20 p-2 rounded border border-amber-900/30">
                    <AlertCircle size={14} className="mt-0.5 shrink-0" />
                    <span>Start `bridge.py` to enable retrieval from your local FAISS index.</span>
                  </div>
                </div>
              )}

            </div>

            <div className="p-6 border-t border-slate-800 bg-slate-900/50 rounded-b-2xl">
              <button
                onClick={() => setIsSettingsOpen(false)}
                className="w-full py-2.5 bg-amber-700 hover:bg-amber-600 text-white font-medium rounded-lg transition-colors"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
