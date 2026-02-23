// frontend/src/App.jsx
import React, { useState } from "react";

const API_BASE = process.env.REACT_APP_API_BASE || (window.__API_BASE__ || (location.protocol.startsWith('http') ? location.origin : 'http://localhost:8000'));

export default function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/triage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto_paciente: text })
      });
      if (!res.ok) {
        const t = await res.text().catch(()=>"");
        setError(`Error HTTP ${res.status}: ${t}`);
        setLoading(false);
        return;
      }
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError("Error de conexión: " + String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Triage Virtual — Demo</h1>

      <form onSubmit={handleSubmit}>
        <textarea
          className="w-full p-3 border rounded mb-3"
          rows={4}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Describe tus síntomas..."
        />
        <button className="px-4 py-2 bg-blue-600 text-white rounded" type="submit" disabled={loading}>
          {loading ? "Analizando..." : "Analizar"}
        </button>
      </form>

      {error && <div className="mt-4 text-red-600">{error}</div>}

      {result && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold">Resultado</h2>
          <p><strong>Recomendación:</strong> {result.recommended_action} (Urgencia {result.overall_urgency})</p>

          <div className="mt-4">
            <h3 className="font-semibold">Síntomas detectados</h3>
            <ul>
              {result.symptoms.map(s => (
                <li key={s.name} className="mt-2 p-2 border rounded">
                  <div><strong>{s.name}</strong> {s.negated ? "(negado)" : ""}</div>
                  <div>Conf: {s.confidence} • Sev: {result.priorities && result.priorities[s.name] ? result.priorities[s.name] : "-" } • Onset: {s.onset || "-"}</div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
} 