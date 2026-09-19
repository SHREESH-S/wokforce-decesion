import React, { useState, useEffect } from 'react';

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export default function App() {
  const [engineers, setEngineers] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [optimization, setOptimization] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE_URL}/engineers`).then(res => res.json()).then(setEngineers);
    fetch(`${API_BASE_URL}/tasks`).then(res => res.json()).then(setTasks);
  }, []);

  const runOptimization = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ engineers, tasks })
      });
      const data = await res.json();
      setOptimization(data);
    } catch (err) {
      console.error("API error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '30px', fontFamily: 'sans-serif', backgroundColor: '#0f172a', color: '#f8fafc', minHeight: '100vh' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '30px', borderBottom: '1px solid #334155', paddingBottom: '15px' }}>
        <h1>⚡ AI Workforce Control Hub</h1>
        <button 
          onClick={runOptimization}
          style={{ padding: '10px 20px', backgroundColor: '#2563eb', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          {loading ? "Processing..." : "Run AI Optimization"}
        </button>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div style={{ backgroundColor: '#1e293b', padding: '20px', borderRadius: '8px' }}>
          <h2>Engineering Resources ({engineers.length})</h2>
          <ul>
            {engineers.map(eng => (
              <li key={eng.id} style={{ marginBottom: '10px' }}>
                <strong>{eng.name}</strong> - Workload: {eng.workload}/{eng.max_capacity} | Rate: ${eng.hourly_rate}/hr
              </li>
            ))}
          </ul>
        </div>

        <div style={{ backgroundColor: '#1e293b', padding: '20px', borderRadius: '8px' }}>
          <h2>Matchmaking Output</h2>
          {optimization ? (
            <ul>
              {optimization.assignments.map((item, i) => (
                <li key={i} style={{ marginBottom: '8px', color: '#38bdf8' }}>
                  {item.task_name} ➔ <strong>{item.assigned_engineer_name}</strong> (Score: {item.match_score})
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ color: '#94a3b8' }}>Click optimization button to execute task assignments.</p>
          )}
        </div>
      </div>
    </div>
  );
}
