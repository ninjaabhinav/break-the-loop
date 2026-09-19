import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";

export default function Dashboard() {
  const navigate = useNavigate();
  const [loops, setLoops] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.listLoops(), api.getAnalytics()])
      .then(([loopData, analyticsData]) => {
        setLoops(loopData);
        setAnalytics(analyticsData);
      })
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div>
      <div className="page-header">
        <div className="eyebrow">Dashboard</div>
        <h1>Your loops</h1>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      {analytics && (
        <div className="stat-grid">
          <div className="card stat-block">
            <div className="stat-value">{analytics.total_urges_logged}</div>
            <div className="stat-label">Urges logged</div>
          </div>
          <div className="card stat-block">
            <div className="stat-value">
              {Math.round(analytics.interruption_rate * 100)}%
            </div>
            <div className="stat-label">Interruption rate</div>
          </div>
          <div className="card stat-block">
            <div className="stat-value">{analytics.most_effective_intervention || "—"}</div>
            <div className="stat-label">Most effective so far</div>
          </div>
        </div>
      )}

      {loops === null && !error && <p>Loading…</p>}

      {loops && loops.length === 0 && (
        <div className="card empty-state">
          <p>You haven't added a behavior loop yet.</p>
          <Link to="/onboarding" className="btn btn-primary">
            Describe a behavior to get started
          </Link>
        </div>
      )}

      {loops &&
        loops.map((loop) => (
          <div className="card" key={loop.id}>
            <div className="card-row">
              <div>
                <h3>{loop.name}</h3>
                <span className="badge badge-accent">{loop.behavior_category.replaceAll("_", " ")}</span>{" "}
                {loop.typical_trigger && <span className="badge">trigger: {loop.typical_trigger}</span>}{" "}
                {loop.typical_context && <span className="badge">context: {loop.typical_context}</span>}
              </div>
              <button
                className="btn btn-primary btn-sm"
                onClick={() => navigate("/urge", { state: { loopId: loop.id } })}
              >
                I'm having an urge
              </button>
            </div>
          </div>
        ))}

      {loops && loops.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <Link to="/onboarding" className="btn btn-secondary btn-sm">
            Add another behavior
          </Link>
        </div>
      )}
    </div>
  );
}
