import React, { useRef } from 'react';

export default function Sidebar({
  documents = [],
  topK = 5,
  setTopK,
  onFileUpload,
  isUploading = false,
}) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onFileUpload(e.target.files[0]);
      e.target.value = '';
    }
  };

  return (
    <aside style={{ display: 'flex', flexDirection: 'column', gap: '20px', minHeight: 0, overflowY: 'auto' }}>
      <div
        style={{
          background: 'linear-gradient(180deg, var(--mint), #f0fdf4)',
          border: '2px solid var(--mint-line)',
          borderRadius: '10px',
          padding: '20px',
        }}
      >
        <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '6px' }}>
          Your knowledge base
        </h2>
        <p style={{ color: 'var(--muted)', fontSize: '14px', marginBottom: '16px' }}>
          Upload the documents the assistant should answer from.
        </p>

        <label
          onClick={() => fileInputRef.current && fileInputRef.current.click()}
          style={{
            display: 'block',
            border: '2px dashed #86efac',
            borderRadius: '8px',
            background: '#fff',
            textAlign: 'center',
            padding: '16px 12px',
            cursor: isUploading ? 'not-allowed' : 'pointer',
            color: 'var(--green-dark)',
            fontWeight: 600,
            fontSize: '14px',
          }}
        >
          {isUploading ? 'Ingesting PDF...' : 'Drop PDF or click to upload'}
          <small style={{ display: 'block', color: 'var(--muted)', fontWeight: 400, fontSize: '12px', marginTop: '4px' }}>
            Supports STG PDF documents
          </small>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            style={{ display: 'none' }}
            disabled={isUploading}
          />
        </label>

        <ul style={{ listStyle: 'none', padding: 0, marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {documents.map((doc, idx) => (
            <li
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                background: '#fff',
                border: '1px solid var(--line)',
                borderRadius: '8px',
                padding: '8px 10px',
                fontSize: '13px',
              }}
            >
              <span
                style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '6px',
                  background: 'var(--green)',
                  display: 'grid',
                  placeItems: 'center',
                  color: '#fff',
                  fontSize: '12px',
                  fontWeight: 600,
                }}
              >
                PDF
              </span>
              <span
                style={{
                  flex: 1,
                  minWidth: 0,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {doc.name}
              </span>
              <span style={{ fontSize: '12px', color: 'var(--green-dark)', fontWeight: 600 }}>
                {doc.status}
              </span>
            </li>
          ))}
        </ul>
      </div>

      <div
        style={{
          background: '#fff',
          border: '1px solid var(--line)',
          borderRadius: '10px',
          padding: '18px 20px',
          boxShadow: 'var(--shadow)',
        }}
      >
        <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '12px' }}>
          Retrieval Settings
        </h3>
        <div>
          <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--muted)', marginBottom: '4px' }}>
            Top-K chunks: {topK}
          </label>
          <input
            type="range"
            min="1"
            max="10"
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            style={{ width: '100%', accentColor: 'var(--green)' }}
          />
        </div>
        <p style={{ fontSize: '12px', color: 'var(--muted)', marginTop: '10px' }}>
          Vector DB: <b>Qdrant (Cosine)</b>
        </p>
      </div>
    </aside>
  );
}
