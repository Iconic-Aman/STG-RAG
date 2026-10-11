import React, { useState } from 'react';
import ChatWindow from '../components/ChatWindow';
import Sidebar from '../components/Sidebar';
import { askQuestion, uploadDocument } from '../api';

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        "Hi, I'm the Edhac assistant. Ask me anything about the documents in your knowledge base and I'll answer with sources.",
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [topK, setTopK] = useState(5);
  const [highlightedCitation, setHighlightedCitation] = useState(null);
  const [documents, setDocuments] = useState([
    { name: 'STANDARD TREATMENT GUIDELINES.pdf', status: 'Indexed' },
  ]);

  const handleSend = async (queryText) => {
    const text = (queryText || input).trim();
    if (!text || isLoading) return;

    const userMessage = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const history = messages.slice(-6).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const res = await askQuestion(text, topK, history);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.answer || 'No answer returned.',
          sources: res.sources || [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error retrieving response: ${err.message}. Ensure backend is running.`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    setIsUploading(true);
    setDocuments((prev) => [...prev, { name: file.name, status: 'Uploading...' }]);
    try {
      await uploadDocument(file);
      setDocuments((prev) =>
        prev.map((d) => (d.name === file.name ? { ...d, status: 'Indexed' } : d))
      );
    } catch (err) {
      setDocuments((prev) =>
        prev.map((d) => (d.name === file.name ? { ...d, status: 'Failed' } : d))
      );
    } finally {
      setIsUploading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: 'Chat cleared. Ask a clinical question to begin.',
      },
    ]);
  };

  return (
    <div className="app-container">
      <header className="nav">
        <div className="brand">
          <svg width="44" height="44" viewBox="0 0 44 44" aria-hidden="true">
            <path d="M15 4h10v11h11v10H25v11H15V25H4V15h11z" fill="#16a34a" />
            <path d="M30 6c-8 2-12 8-12 16" stroke="#84cc16" strokeWidth="4" fill="none" strokeLinecap="round" />
          </svg>
          <div>
            <span className="brand-name">edhac</span>
            <span className="brand-tag">TRANSFORMING PATIENT CARE</span>
          </div>
        </div>
        <div className="nav-right">
          <span className="status">
            <span className="dot" />
            <span>Knowledge base ready</span>
          </span>
          <button className="btn btn-outline" onClick={handleClearChat}>
            Clear chat
          </button>
        </div>
      </header>

      <main className="page">
        <ChatWindow
          messages={messages}
          input={input}
          setInput={setInput}
          onSend={() => handleSend(input)}
          isLoading={isLoading}
          highlightedCitation={highlightedCitation}
          setHighlightedCitation={setHighlightedCitation}
          onSuggestionClick={(sug) => handleSend(sug)}
        />
        <Sidebar
          documents={documents}
          topK={topK}
          setTopK={setTopK}
          onFileUpload={handleFileUpload}
          isUploading={isUploading}
        />
      </main>
    </div>
  );
}
