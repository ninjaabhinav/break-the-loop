import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function History() {
  const [events, setEvents] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.listEvents().then(setEvents).catch((err) => setError(err.message));
  }, []);

  return (
    <div>
      <div className="page-header">
        <div className="eyebrow">History</div>
        <h1>Past urges</h1>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}
      {events === null && !error && <p>Loading…</p>}
      {events && events.length === 0 && (
        <div className="card empty-state">
          <p>No urges logged yet.</p>
        </div>
      )}

      {events && events.length > 0 && (
        <div className="card" style={{ overflowX: "auto" }}>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Trigger</th>
                <th>Context</th>
                <th>Emotion</th>
                <th>Urge</th>
                <th>Completed</th>
                <th>Behavior occurred</th>
                <th>Urge after</th>
                <th>Method</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e) => (
                <tr key={e.id}>
                  <td>{new Date(e.created_at).toLocaleString()}</td>
                  <td>{e.trigger}</td>
                  <td>{e.context}</td>
                  <td>{e.emotion}</td>
                  <td>{e.urge_intensity}</td>
                  <td>{fmtBool(e.intervention_completed)}</td>
                  <td>{fmtBool(e.behavior_occurred)}</td>
                  <td>{e.post_intervention_urge ?? "—"}</td>
                  <td>{e.recommendation_method ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function fmtBool(value) {
  if (value === null || value === undefined) return "—";
  return value ? "Yes" : "No";
}
