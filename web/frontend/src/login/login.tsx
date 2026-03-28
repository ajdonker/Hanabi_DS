import { type FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getEventData, wsClient } from "../network/wsClient";
import { PLAY_LOGIN_COMMAND } from "../network/commandTypes";
import "./login.css";

type PlayerLoggedEvent = {
  playerId: string;
  username: string;
};

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [message, setMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = username.trim();
    if (!trimmed) {
      setMessage("Please enter a username.");
      return;
    }
    if (isSubmitting) {
      return;
    }

    try {
      setIsSubmitting(true);
      setMessage("");
      const events = await wsClient.command<{ username: string }>(
        PLAY_LOGIN_COMMAND,
        { username: trimmed },
      );

      const result = getEventData<PlayerLoggedEvent>(events, "player_logged");
      if (!result) {
        setMessage("Login failed: invalid server response.");
        return;
      }

      localStorage.setItem("hanabi.playerId", result.playerId);
      localStorage.setItem("hanabi.username", result.username);
      navigate("/lobby");
    } catch (error) {
      console.error("Failed to submit login:", error);
      setMessage(error instanceof Error ? error.message : "Unable to reach backend.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="login-page">
      <div className="login-card">
        <p className="login-eyebrow">HANABI</p>
        <h2>Login</h2>
        <form className="login-form" onSubmit={handleSubmit}>
          <label className="login-field">
            <input
              type="text"
              placeholder="Please enter a username"
              value={username}
              onChange={(event) => {
                setUsername(event.target.value);
                if (message) {
                  setMessage("");
                }
              }}
              autoComplete="username"
            />
          </label>
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Logging in..." : "Login"}
          </button>
        </form>
        {message && (
          <p className="login-message is-error">{message}</p>
        )}
      </div>
    </section>
  );
}
