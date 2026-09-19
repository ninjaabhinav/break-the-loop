import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import Timer from "../components/Timer.jsx";

const STEPS = ["context", "recommendation", "timer", "outcome", "done"];

export default function UrgeFlow() {
  const location = useLocation();
  const navigate = useNavigate();

  const [step, setStep] = useState("context");
  const [loops, setLoops] = useState([]);
  const [loopId, setLoopId] = useState(location.state?.loopId || "");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const [form, setForm] = useState({ trigger: "", context: "", emotion: "", urge_intensity: 5 });
  const [recommendation, setRecommendation] = useState(null);
  const [selectedIntervention, setSelectedIntervention] = useState(null);
  const [startedAt, setStartedAt] = useState(null);

  const [outcome, setOutcome] = useState({
    intervention_completed: true,
    post_intervention_urge: 3,
    behavior_occurred: false,
    user_rating: 4,
  });

  useEffect(() => {
    api.listLoops().then(setLoops).catch((err) => setError(err.message));
  }, []);

  function updateForm(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleLogUrge(e) {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const payload = { ...form, loop_id: loopId || null, urge_intensity: Number(form.urge_intensity) };
      const rec = await api.logUrge(payload);
      setRecommendation(rec);
      setStep("recommendation");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handlePickIntervention(intervention) {
    setSubmitting(true);
    setError("");
    try {
      await api.selectIntervention(recommendation.event_id, intervention.id);
      setSelectedIntervention(intervention);
      setStartedAt(Date.now());
      setStep("timer");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  function handleTimerFinish() {
    setStep("outcome");
  }

  async function handleSubmitOutcome(e) {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const delayMinutes = startedAt ? (Date.now() - startedAt) / 60000 : null;
      await api.reportOutcome(recommendation.event_id, {
        ...outcome,
        post_intervention_urge: Number(outcome.post_intervention_urge),
        user_rating: Number(outcome.user_rating),
        delay_minutes: delayMinutes ? Math.round(delayMinutes * 10) / 10 : null,
      });
      setStep("done");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  const stepIndex = STEPS.indexOf(step);

  return (
    <div>
      <div className="page-header">
        <div className="eyebrow">Log an urge</div>
        <h1>What's happening right now?</h1>
      </div>

      <div className="step-indicator">
        {STEPS.map((s, i) => (
          <div key={s} className={`step-dot${i <= stepIndex ? " active" : ""}`} />
        ))}
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      {step === "context" && (
        <form className="card form-narrow" onSubmit={handleLogUrge}>
          {loops.length > 0 && (
            <div className="field">
              <label htmlFor="loop">Which behavior loop is this?</label>
              <select id="loop" value={loopId} onChange={(e) => setLoopId(e.target.value)}>
                <option value="">Not sure / general</option>
                {loops.map((l) => (
                  <option key={l.id} value={l.id}>
                    {l.name}
                  </option>
                ))}
              </select>
            </div>
          )}
          <div className="field">
            <label htmlFor="trigger">What triggered this?</label>
            <input
              id="trigger"
              value={form.trigger}
              onChange={(e) => updateForm("trigger", e.target.value)}
              placeholder="e.g. stress"
              required
            />
          </div>
          <div className="field">
            <label htmlFor="context">Where are you / what's the situation?</label>
            <input
              id="context"
              value={form.context}
              onChange={(e) => updateForm("context", e.target.value)}
              placeholder="e.g. studying"
              required
            />
          </div>
          <div className="field">
            <label htmlFor="emotion">What are you feeling?</label>
            <input
              id="emotion"
              value={form.emotion}
              onChange={(e) => updateForm("emotion", e.target.value)}
              placeholder="e.g. anxious"
              required
            />
          </div>
          <div className="field">
            <label>Urge intensity: {form.urge_intensity} / 10</label>
            <div className="intensity-scale">
              {Array.from({ length: 10 }, (_, i) => i + 1).map((n) => (
                <div
                  key={n}
                  className={`intensity-option${Number(form.urge_intensity) === n ? " selected" : ""}`}
                  onClick={() => updateForm("urge_intensity", n)}
                >
                  {n}
                </div>
              ))}
            </div>
          </div>
          <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
            {submitting ? "Finding an intervention…" : "Get a recommendation"}
          </button>
        </form>
      )}

      {step === "recommendation" && recommendation && (
        <div>
          <div className="card">
            <span className="badge badge-accent">
              {recommendation.method === "ml" ? "personalized recommendation" : "starting recommendation"}
            </span>
            <h2 style={{ marginTop: 12 }}>{recommendation.primary.intervention.name}</h2>
            <p>{recommendation.primary.intervention.description}</p>
            <p className="field-hint">
              {recommendation.primary.intervention.duration_minutes} min ·{" "}
              {recommendation.primary.intervention.difficulty} · estimated fit{" "}
              {Math.round(recommendation.primary.score * 100)}%
            </p>
            <button
              className="btn btn-primary"
              disabled={submitting}
              onClick={() => handlePickIntervention(recommendation.primary.intervention)}
            >
              Try this
            </button>
          </div>

          {recommendation.backups.length > 0 && (
            <div className="card">
              <h3>Other options</h3>
              {recommendation.backups.map((b) => (
                <div className="card-row" key={b.intervention.id} style={{ marginBottom: 10 }}>
                  <div>
                    <strong>{b.intervention.name}</strong>
                    <div className="field-hint">
                      {b.intervention.duration_minutes} min · estimated fit {Math.round(b.score * 100)}%
                    </div>
                  </div>
                  <button
                    className="btn btn-secondary btn-sm"
                    disabled={submitting}
                    onClick={() => handlePickIntervention(b.intervention)}
                  >
                    Try this instead
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {step === "timer" && selectedIntervention && (
        <div className="card" style={{ textAlign: "center" }}>
          <h2>{selectedIntervention.name}</h2>
          <p>{selectedIntervention.description}</p>
          <Timer totalSeconds={selectedIntervention.duration_minutes * 60} onFinish={handleTimerFinish} />
        </div>
      )}

      {step === "outcome" && (
        <form className="card form-narrow" onSubmit={handleSubmitOutcome}>
          <h2>How did it go?</h2>
          <div className="field">
            <label>Did you complete the intervention?</label>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                type="button"
                className={`btn ${outcome.intervention_completed ? "btn-primary" : "btn-secondary"} btn-sm`}
                onClick={() => setOutcome((p) => ({ ...p, intervention_completed: true }))}
              >
                Yes
              </button>
              <button
                type="button"
                className={`btn ${!outcome.intervention_completed ? "btn-primary" : "btn-secondary"} btn-sm`}
                onClick={() => setOutcome((p) => ({ ...p, intervention_completed: false }))}
              >
                No
              </button>
            </div>
          </div>
          <div className="field">
            <label>Did the original behavior still happen?</label>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                type="button"
                className={`btn ${!outcome.behavior_occurred ? "btn-primary" : "btn-secondary"} btn-sm`}
                onClick={() => setOutcome((p) => ({ ...p, behavior_occurred: false }))}
              >
                No, I interrupted it
              </button>
              <button
                type="button"
                className={`btn ${outcome.behavior_occurred ? "btn-primary" : "btn-secondary"} btn-sm`}
                onClick={() => setOutcome((p) => ({ ...p, behavior_occurred: true }))}
              >
                Yes, it happened anyway
              </button>
            </div>
          </div>
          <div className="field">
            <label htmlFor="post_urge">Urge intensity now (1-10)</label>
            <input
              id="post_urge"
              type="number"
              min="1"
              max="10"
              value={outcome.post_intervention_urge}
              onChange={(e) => setOutcome((p) => ({ ...p, post_intervention_urge: e.target.value }))}
            />
          </div>
          <div className="field">
            <label htmlFor="rating">How helpful was this? (1-5)</label>
            <input
              id="rating"
              type="number"
              min="1"
              max="5"
              value={outcome.user_rating}
              onChange={(e) => setOutcome((p) => ({ ...p, user_rating: e.target.value }))}
            />
          </div>
          <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
            {submitting ? "Saving…" : "Save outcome"}
          </button>
        </form>
      )}

      {step === "done" && (
        <div className="card empty-state">
          <p>Logged. Every outcome like this helps the recommendations get more personal.</p>
          <button className="btn btn-primary" onClick={() => navigate("/dashboard")}>
            Back to dashboard
          </button>
        </div>
      )}
    </div>
  );
}
