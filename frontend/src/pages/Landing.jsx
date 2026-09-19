import { Link } from "react-router-dom";

const STEPS = [
  { title: "Trigger", body: "Something in your environment or state sets things off — stress, boredom, a place, a time of day." },
  { title: "Urge", body: "A pull toward a specific behavior builds, often within seconds." },
  { title: "Automatic behavior", body: "The behavior happens with little deliberate choice involved." },
  { title: "Short-term reward", body: "Relief, distraction, or comfort — enough to reinforce the pattern." },
  { title: "Long-term cost", body: "The behavior works against something you actually care about." },
  { title: "Repetition", body: "The same trigger shows up again, and the loop runs once more." },
];

export default function Landing() {
  return (
    <div className="landing">
      <div className="landing-hero">
        <h1>Interrupt the loop before it runs again.</h1>
        <p>
          Break the Loop helps you notice the trigger behind a habit you want to change, and
          offers one small, specific action to try in the moment — instead of just telling you
          to stop.
        </p>
        <div className="landing-actions">
          <Link to="/register" className="btn btn-primary">
            Create an account
          </Link>
          <Link to="/login" className="btn btn-secondary">
            Sign in
          </Link>
        </div>
      </div>

      <div className="loop-sequence">
        <h2>Every unwanted habit runs on the same sequence</h2>
        <ol className="loop-sequence-list">
          {STEPS.map((step, i) => (
            <li className="loop-sequence-item" key={step.title}>
              <span className="loop-sequence-index">{i + 1}</span>
              <div className="loop-sequence-body">
                <h3>{step.title}</h3>
                <p>{step.body}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>

      <p className="field-hint">
        Break the Loop is an experimental behavioral-support tool, not a medical treatment. If
        you're dealing with addiction or a mental-health condition, please also talk to a
        qualified professional.
      </p>
    </div>
  );
}
