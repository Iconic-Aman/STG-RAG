const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export async function askQuestion(query, topK = 5, history = []) {
  if (!API_BASE) {
    throw new Error('API URL not configured in environment variable.');
  }

  const response = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      top_k: topK,
      history,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with code ${response.status}`);
  }

  return response.json();
}

export async function uploadDocument(file) {
  if (!API_BASE) {
    throw new Error('API URL not configured in environment variable.');
  }

  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/ingest`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload failed with code ${response.status}`);
  }

  return response.json();
}
