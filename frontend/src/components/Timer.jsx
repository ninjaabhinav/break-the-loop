import { useEffect, useRef, useState } from "react";

export default function Timer({ totalSeconds, onFinish }) {
  const [remaining, setRemaining] = useState(totalSeconds);
  const [running, setRunning] = useState(true);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!running) return undefined;
    intervalRef.current = setInterval(() => {
      setRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(intervalRef.current);
          onFinish?.();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(intervalRef.current);
  }, [running, onFinish]);

  const minutes = String(Math.floor(remaining / 60)).padStart(2, "0");
  const seconds = String(remaining % 60).padStart(2, "0");

  return (
    <div>
      <div className="timer-display">
        {minutes}:{seconds}
      </div>
      <div style={{ display: "flex", gap: 8, justifyContent: "center" }}>
        <button className="btn btn-secondary btn-sm" onClick={() => setRunning((r) => !r)}>
          {running ? "Pause" : "Resume"}
        </button>
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => {
            setRunning(false);
            onFinish?.();
          }}
        >
          I'm done early
        </button>
      </div>
    </div>
  );
}
