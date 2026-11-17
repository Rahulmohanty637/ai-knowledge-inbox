import { useEffect, useState } from "react";

function App() {
  const [health, setHealth] = useState<string>("checking...");

  useEffect(() => {
    fetch("/api/health")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => setHealth(data.status))
      .catch(() => setHealth("API not reachable"));
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 p-8">
      <h1 className="text-2xl font-semibold text-slate-900">
        AI Knowledge Inbox
      </h1>
      <p className="mt-2 text-slate-600">
        API status: <span className="font-mono">{health}</span>
      </p>
    </main>
  );
}

export default App;
