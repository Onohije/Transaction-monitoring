import React, { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Activity, Database, FileText, Play, RefreshCw } from "lucide-react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function api(path, options) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) throw new Error(`API ${response.status}`);
  return response.json();
}

function Stat({ icon: Icon, label, value }) {
  return (
    <section className="stat">
      <Icon size={18} />
      <span>{label}</span>
      <strong>{value}</strong>
    </section>
  );
}

function App() {
  const [summary, setSummary] = useState({ total: 0, by_status: {} });
  const [transactions, setTransactions] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  const failedRate = useMemo(() => {
    if (!summary.total) return "0.0%";
    return `${((summary.failed / summary.total) * 100).toFixed(1)}%`;
  }, [summary]);

  async function load() {
    const [summaryData, txData, alertData, logData] = await Promise.all([
      api("/summary"),
      api(`/transactions${status ? `?status=${status}` : ""}`),
      api("/alerts"),
      api("/logs?limit=50"),
    ]);
    setSummary(summaryData);
    setTransactions(txData);
    setAlerts(alertData);
    setLogs(logData);
  }

  async function simulate() {
    setBusy(true);
    try {
      await api("/simulate", { method: "POST", body: JSON.stringify({ count: 40 }) });
      await load();
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    load();
    const timer = setInterval(load, 10000);
    return () => clearInterval(timer);
  }, [status]);

  return (
    <main>
      <header className="topbar">
        <div>
          <h1>Transaction Monitoring</h1>
          <p>Core banking operations dashboard for transaction status, failures, alerts, and audit logs.</p>
        </div>
        <div className="actions">
          <button onClick={simulate} disabled={busy}><Play size={16} /> Simulate</button>
          <button onClick={load}><RefreshCw size={16} /> Refresh</button>
        </div>
      </header>

      <section className="stats">
        <Stat icon={Database} label="Total" value={summary.total} />
        <Stat icon={Activity} label="Settled" value={summary.settled || 0} />
        <Stat icon={AlertTriangle} label="Failed" value={summary.failed || 0} />
        <Stat icon={FileText} label="Failure Rate" value={failedRate} />
      </section>

      <section className="toolbar">
        {["", "SETTLED", "FAILED", "POSTED", "VALIDATED"].map((item) => (
          <button key={item || "ALL"} className={status === item ? "active" : ""} onClick={() => setStatus(item)}>
            {item || "ALL"}
          </button>
        ))}
      </section>

      <section className="grid">
        <div className="panel wide">
          <h2>Transaction Status</h2>
          <table>
            <thead>
              <tr><th>Reference</th><th>Channel</th><th>Amount</th><th>Status</th><th>Reason</th></tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.id}>
                  <td>{tx.reference}</td>
                  <td>{tx.channel}</td>
                  <td>{tx.currency} {Number(tx.amount).toLocaleString()}</td>
                  <td><span className={`pill ${tx.status.toLowerCase()}`}>{tx.status}</span></td>
                  <td>{tx.failure_reason || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="panel">
          <h2>Alerts</h2>
          <div className="list">
            {alerts.map((alert) => (
              <article key={alert.id}>
                <strong>{alert.title}</strong>
                <p>{alert.message}</p>
                <small>{new Date(alert.created_at).toLocaleString()}</small>
              </article>
            ))}
          </div>
        </div>

        <div className="panel wide">
          <h2>Audit Logs</h2>
          <div className="logs">
            {logs.map((log) => (
              <div key={log.id}>
                <time>{new Date(log.created_at).toLocaleTimeString()}</time>
                <code>{log.event_type}</code>
                <span>{log.message}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);

