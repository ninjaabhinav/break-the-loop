import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Analytics() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getAnalytics().then(setData).catch((err) => setError(err.message));
  }, []);

  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!data) return <p>Loading…</p>;

  const maxUsage = Math.max(1, ...data.intervention_breakdown.map((b) => b.times_used));
  const maxTrigger = Math.max(1, ...data.trigger_breakdown.map((t) => t.count));

  return (
    <div>
      <div className="page-header">
        <div className="eyebrow">Analytics</div>
        <h1>How it's going</h1>
      </div>

      <div className="stat-grid">
        <Stat label="Baseline frequency / day" value={fmt(data.baseline_frequency_per_day)} />
        <Stat label="Current frequency / day (last 7d)" value={fmt(data.current_frequency_per_day)} />
        <Stat label="Urges logged" value={data.total_urges_logged} />
        <Stat label="Interventions attempted" value={data.interventions_attempted} />
        <Stat label="Successful interruptions" value={data.successful_interruptions} />
        <Stat label="Interruption rate" value={`${Math.round(data.interruption_rate * 100)}%`} />
        <Stat label="Avg. urge before" value={fmt(data.average_urge_before)} />
        <Stat label="Avg. urge after" value={fmt(data.average_urge_after)} />
        <Stat label="Avg. delay (min)" value={fmt(data.average_delay_minutes)} />
      </div>

      <div className="card">
        <h3>Intervention effectiveness</h3>
        {data.intervention_breakdown.length === 0 && (
          <p className="field-hint">No completed interventions yet.</p>
        )}
        {data.intervention_breakdown.map((b) => (
          <div className="bar-row" key={b.intervention_name}>
            <div className="bar-label">{b.intervention_name}</div>
            <div className="bar-track">
              <div className="bar-fill" style={{ width: `${(b.times_used / maxUsage) * 100}%` }} />
            </div>
            <div className="bar-value">{Math.round(b.success_rate * 100)}%</div>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>Most common triggers</h3>
        {data.trigger_breakdown.length === 0 && <p className="field-hint">No urges logged yet.</p>}
        {data.trigger_breakdown.map((t) => (
          <div className="bar-row" key={t.trigger}>
            <div className="bar-label">{t.trigger}</div>
            <div className="bar-track">
              <div className="bar-fill" style={{ width: `${(t.count / maxTrigger) * 100}%` }} />
            </div>
            <div className="bar-value">{t.count}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="card stat-block">
      <div className="stat-value">{value ?? "—"}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function fmt(value) {
  return value === null || value === undefined ? "—" : value;
}
