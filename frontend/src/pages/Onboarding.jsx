import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";

const CATEGORY_OPTIONS = [
  "smoking",
  "doomscrolling",
  "gaming",
  "procrastination",
  "overthinking",
  "unhealthy_eating",
  "other",
];

const INITIAL_ASSISTANT_MESSAGE = {
  role: "assistant",
  content:
    "Tell me about a behavior you'd like to change. For example: \"I always start scrolling " +
    "Instagram when I'm stressed while studying.\"",
};

export default function Onboarding() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([INITIAL_ASSISTANT_MESSAGE]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);

  const [fields, setFields] = useState({
    name: "",
    behavior_category: "",
    typical_trigger: "",
    typical_context: "",
    typical_emotion: "",
    frequency_description: "",
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function mergeExtracted(extracted) {
    setFields((prev) => ({
      name: prev.name || extracted.behavior?.replaceAll("_", " ") || "",
      behavior_category: extracted.behavior_category || prev.behavior_category,
      typical_trigger: extracted.trigger || prev.typical_trigger,
      typical_context: extracted.context || prev.typical_context,
      typical_emotion: extracted.emotion || prev.typical_emotion,
      frequency_description: extracted.frequency_description || prev.frequency_description,
    }));
  }

  async function handleSend(e) {
    e.preventDefault();
    if (!input.trim() || sending) return;
    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setSending(true);
    setError("");
    try {
      const result = await api.sendOnboardingMessage(userMessage.content);
      setMessages((prev) => [...prev, { role: "assistant", content: result.reply }]);
      mergeExtracted(result.extracted);
    } catch (err) {
      setError(err.message);
    } finally {
      setSending(false);
    }
  }

  function handleFieldChange(field, value) {
    setFields((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSaveLoop(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await api.createLoop(fields);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  const canSave = fields.name.trim() && fields.behavior_category;

  return (
    <div>
      <div className="page-header">
        <div className="eyebrow">Add a behavior</div>
        <h1>Describe what you want to change</h1>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <div style={{ display: "grid", gridTemplateColumns: "1.3fr 1fr", gap: 20 }}>
        <div className="chat-window">
          <div className="chat-messages">
            {messages.map((m, i) => (
              <div key={i} className={`chat-message ${m.role}`}>
                {m.content}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <form className="chat-input-row" onSubmit={handleSend}>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  handleSend(e);
                }
              }}
              placeholder="Describe the behavior, trigger, and how it feels…"
            />
            <button type="submit" className="btn btn-primary" disabled={sending}>
              Send
            </button>
          </form>
        </div>

        <div className="card">
          <h3>What I've picked up so far</h3>
          <form onSubmit={handleSaveLoop}>
            <div className="field">
              <label htmlFor="name">Loop name</label>
              <input
                id="name"
                value={fields.name}
                onChange={(e) => handleFieldChange("name", e.target.value)}
                placeholder="e.g. Doomscrolling while studying"
              />
            </div>
            <div className="field">
              <label htmlFor="behavior_category">Category</label>
              <select
                id="behavior_category"
                value={fields.behavior_category}
                onChange={(e) => handleFieldChange("behavior_category", e.target.value)}
              >
                <option value="">Select one</option>
                {CATEGORY_OPTIONS.map((c) => (
                  <option key={c} value={c}>
                    {c.replaceAll("_", " ")}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="trigger">Typical trigger</label>
              <input
                id="trigger"
                value={fields.typical_trigger}
                onChange={(e) => handleFieldChange("typical_trigger", e.target.value)}
                placeholder="e.g. stress"
              />
            </div>
            <div className="field">
              <label htmlFor="context">Typical context</label>
              <input
                id="context"
                value={fields.typical_context}
                onChange={(e) => handleFieldChange("typical_context", e.target.value)}
                placeholder="e.g. studying"
              />
            </div>
            <div className="field">
              <label htmlFor="emotion">Typical emotion</label>
              <input
                id="emotion"
                value={fields.typical_emotion}
                onChange={(e) => handleFieldChange("typical_emotion", e.target.value)}
                placeholder="e.g. anxious"
              />
            </div>
            <div className="field">
              <label htmlFor="frequency">Frequency</label>
              <input
                id="frequency"
                value={fields.frequency_description}
                onChange={(e) => handleFieldChange("frequency_description", e.target.value)}
                placeholder="e.g. several times a day"
              />
            </div>
            <button type="submit" className="btn btn-primary btn-block" disabled={!canSave || saving}>
              {saving ? "Saving…" : "Save this behavior loop"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
