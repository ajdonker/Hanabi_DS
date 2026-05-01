import { type FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getEventData, wsClient } from "../network/wsClient";
import { PLAY_LOGIN_COMMAND } from "../network/commandTypes";
import {
  LOGIN_SUCCESS_EVENT,
  PLAYER_RECONNECTED_EVENT,
} from "../network/eventTypes";
import "./login.css";

type LoginSuccessEvent = {
  message: string;
  player_name: string;
};

type PlayerReconnectedEvent = {
  player_name: string;
  game_id: string;
  host: string;
  port: number;
};

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedUsername = username.trim();
    if (isSubmitting) {
      return;
    }

    if (!trimmedUsername || !password) {
      setMessage("Please enter username and password.");
      return;
    }

    try {
      setIsSubmitting(true);
      setMessage("");
      const data = {
        username: trimmedUsername,
        password,
      };
      const events = await wsClient.command<typeof data>(
        PLAY_LOGIN_COMMAND,
        data,
      );

      const login = getEventData<LoginSuccessEvent>(events, LOGIN_SUCCESS_EVENT);
      if (login) {
        localStorage.setItem("hanabi.playerId", login.player_name);
        localStorage.setItem("hanabi.username", login.player_name);
        navigate("/lobby");
        return;
      }

      const reconnect = getEventData<PlayerReconnectedEvent>(
        events,
        PLAYER_RECONNECTED_EVENT,
      );
      if (reconnect) {
        localStorage.setItem("hanabi.playerId", reconnect.player_name);
        localStorage.setItem("hanabi.username", reconnect.player_name);
        localStorage.setItem(
          "hanabi.gameWsUrl",
          `ws://${reconnect.host}:${reconnect.port}/ws`,
        );
        navigate(`/game/${reconnect.game_id}`);
        return;
      }

      setMessage("Login failed: invalid server response.");
      return;
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
              placeholder="Username"
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
          <label className="login-field">
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                if (message) {
                  setMessage("");
                }
              }}
              autoComplete="current-password"
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
