import React, { useRef, useEffect } from 'react';
import CitationPanel from './CitationPanel';

export default function ChatWindow({
  messages = [],
  input = '',
  setInput,
  onSend,
  isLoading = false,
  highlightedCitation,
  setHighlightedCitation,
  onSuggestionClick,
}) {
  const msgsEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    msgsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  const renderContentWithCitations = (content, sources = []) => {
    const parts = content.split(/(\[\d+\])/g);
    return parts.map((part, i) => {
      const match = part.match(/\[(\d+)\]/);
      if (match) {
        const id = parseInt(match[1], 10);
        return (
          <button
            key={i}
            onClick={() => {
              setHighlightedCitation(id);
              const el = document.getElementById(`source-${id}`);
              el?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }}
            style={{
              display: 'inline-grid',
              placeItems: 'center',
              minWidth: '20px',
              height: '20px',
              padding: '0 5px',
              margin: '0 2px',
              borderRadius: '5px',
              background: 'var(--mint)',
              border: '1px solid var(--mint-line)',
              color: 'var(--green-dark)',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
              verticalAlign: 'baseline',
            }}
          >
            {id}
          </button>
        );
      }
      return part;
    });
  };

  const suggestions = [
    'First-line treatment for uncomplicated malaria?',
    'Dosage of Artemether-lumefantrine in children?',
    'Management of severe pneumonia?',
  ];

  return (
    <section
      style={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: 0,
        background: 'var(--card)',
        border: '1px solid var(--line)',
        borderRadius: '10px',
        boxShadow: 'var(--shadow)',
      }}
    >
      <div style={{ padding: '18px 22px', borderBottom: '1px solid var(--line)', display: 'flex', gap: '14px', alignItems: 'center' }}>
        <div style={{ width: '44px', height: '44px', borderRadius: '8px', background: 'var(--green)', display: 'grid', placeItems: 'center', flex: 'none' }}>
          <svg viewBox="0 0 24 24" width="22" height="22" stroke="#fff" fill="none" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.8 0-3 .5-4.5 2-1.5-1.5-2.7-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4 3 5.5l7 7z" />
          </svg>
        </div>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: 700, lineHeight: 1.2 }}>Ask Edhac</h1>
          <p style={{ fontSize: '14px', color: 'var(--muted)' }}>Answers come from your documents, with sources shown.</p>
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              gap: '12px',
              maxWidth: '88%',
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
            }}
          >
            <div
              style={{
                padding: '12px 16px',
                borderRadius: '10px',
                border: '1px solid var(--line)',
                background: msg.role === 'user' ? 'var(--green)' : 'var(--bg)',
                color: msg.role === 'user' ? '#fff' : 'var(--ink)',
                whiteSpace: 'pre-wrap',
                wordWrap: 'break-word',
              }}
            >
              {msg.role === 'user' ? msg.content : renderContentWithCitations(msg.content, msg.sources)}
              {msg.role === 'assistant' && msg.sources && (
                <CitationPanel
                  sources={msg.sources}
                  highlightedId={highlightedCitation}
                  onCitationClick={(id) => setHighlightedCitation(id)}
                />
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div style={{ display: 'flex', gap: '12px', alignSelf: 'flex-start' }}>
            <div style={{ padding: '12px 16px', borderRadius: '10px', background: 'var(--bg)', color: 'var(--muted)', fontSize: '14px' }}>
              Searching guidelines and generating citations...
            </div>
          </div>
        )}
        <div ref={msgsEndRef} />
      </div>

      {messages.length <= 1 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', padding: '0 20px 12px' }}>
          {suggestions.map((sug, i) => (
            <button
              key={i}
              onClick={() => onSuggestionClick(sug)}
              style={{
                background: '#fff',
                border: '1px solid var(--mint-line)',
                color: 'var(--green-dark)',
                borderRadius: '999px',
                padding: '6px 14px',
                fontSize: '13px',
              }}
            >
              {sug}
            </button>
          ))}
        </div>
      )}

      <div style={{ display: 'flex', gap: '10px', padding: '16px 20px', borderTop: '1px solid var(--line)' }}>
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a clinical question (e.g. malaria treatment)..."
          style={{
            flex: 1,
            resize: 'none',
            border: '1px solid var(--line)',
            borderRadius: '8px',
            padding: '10px 14px',
            font: 'inherit',
            maxHeight: '120px',
            background: '#fff',
            color: 'var(--ink)',
          }}
        />
        <button
          onClick={onSend}
          disabled={isLoading || !input.trim()}
          style={{
            background: 'var(--green)',
            color: '#fff',
            border: 0,
            borderRadius: '8px',
            padding: '0 20px',
            fontWeight: 600,
            fontSize: '15px',
            opacity: isLoading || !input.trim() ? 0.5 : 1,
            cursor: isLoading || !input.trim() ? 'not-allowed' : 'pointer',
          }}
        >
          Send
        </button>
      </div>
    </section>
  );
}
