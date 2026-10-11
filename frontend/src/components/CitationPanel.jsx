import React from 'react';

export default function CitationPanel({
  sources = [],
  highlightedId,
  onCitationClick,
}) {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--muted)' }}>
        Sources & Citations
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {sources.map((src, index) => {
          const id = src.id ?? index + 1;
          const isHighlighted = highlightedId === id;

          return (
            <div
              key={id}
              id={`source-${id}`}
              onClick={() => onCitationClick && onCitationClick(id)}
              style={{
                background: isHighlighted ? 'var(--mint)' : '#fff',
                border: '1px solid var(--line)',
                borderLeft: '3px solid var(--green)',
                borderRadius: '6px',
                padding: '8px 12px',
                fontSize: '14px',
                cursor: 'pointer',
                transition: 'background 0.2s',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <b style={{ fontWeight: 600 }}>
                  [{id}] {src.section || 'General Guideline'}
                </b>
                {src.score != null && (
                  <span style={{ fontSize: '12px', color: 'var(--green-dark)', fontWeight: 600 }}>
                    {Math.round(src.score * 100)}% match
                  </span>
                )}
              </div>
              {src.page && (
                <div style={{ fontSize: '12px', color: 'var(--muted)', marginTop: '2px' }}>
                  Page: {src.page}
                </div>
              )}
              {src.snippet && (
                <small
                  style={{
                    display: 'block',
                    color: 'var(--muted)',
                    fontSize: '13px',
                    marginTop: '4px',
                    lineHeight: 1.4,
                  }}
                >
                  {src.snippet}
                </small>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
