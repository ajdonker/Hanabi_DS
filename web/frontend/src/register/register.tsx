import { type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { PLAYER_REGISTER_COMMAND } from "../network/commandTypes";
import { ERROR_EVENT, REGISTRATION_SUCCESS_EVENT } from "../network/eventTypes";
import { getEventData, wsClient } from "../network/wsClient";
import "../login/login.css";
import "./register.css";

type RegisterPayload = {
  fullName: string;
  email: string;
  username: string;
  password: string;
};

type ServerMessageEvent = {
  message?: string;
};

export default function Register() {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"error" | "success">("error");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function clearMessage() {
    if (message) {
      setMessage("");
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (isSubmitting) {
      return;
    }

    const payload: RegisterPayload = {
      fullName: fullName.trim(),
      email: email.trim(),
      username: username.trim(),
      password,
    };

    if (!payload.fullName || !payload.email || !payload.username || !payload.password) {
      setMessageType("error");
      setMessage("Please fill in every field.");
      return;
    }

    try {
      setIsSubmitting(true);
      setMessage("");

      const events = await wsClient.command<RegisterPayload>(
        PLAYER_REGISTER_COMMAND,
        payload,
      );

      const error = getEventData<ServerMessageEvent>(events, ERROR_EVENT);
      if (error) {
        setMessageType("error");
        setMessage(error.message || "Registration failed.");
        return;
      }

      const result = getEventData<ServerMessageEvent>(
        events,
        REGISTRATION_SUCCESS_EVENT,
      );
      if (!result) {
        setMessageType("error");
        setMessage("Registration failed: invalid server response.");
        return;
      }

      setMessageType("success");
      setMessage(result.message || "Registration successful.");
      window.setTimeout(() => {
        navigate("/login");
      }, 700);
    } catch (error) {
      console.error("Failed to submit registration:", error);
      setMessageType("error");
      setMessage(error instanceof Error ? error.message : "Unable to reach backend.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="login-page register-page">
      <div className="login-card register-card">
        <p className="login-eyebrow">HANABI</p>
        <h2>Create Account</h2>
        <form className="login-form register-form" onSubmit={handleSubmit}>
          <label className="login-field">
            <span>Full Name</span>
            <input
              type="text"
              placeholder="full name"
              value={fullName}
              onChange={(event) => {
                setFullName(event.target.value);
                clearMessage();
              }}
              autoComplete="name"
            />
          </label>
          <label className="login-field">
            <span>Email</span>
            <input
              type="email"
              placeholder="name@example.com"
              value={email}
              onChange={(event) => {
                setEmail(event.target.value);
                clearMessage();
              }}
              autoComplete="email"
            />
          </label>
          <label className="login-field">
            <span>Username</span>
            <input
              type="text"
              placeholder="ada"
              value={username}
              onChange={(event) => {
                setUsername(event.target.value);
                clearMessage();
              }}
              autoComplete="username"
            />
          </label>
          <label className="login-field">
            <span>Password</span>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                clearMessage();
              }}
              autoComplete="new-password"
            />
          </label>
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating..." : "Register"}
          </button>
        </form>
        {message && (
          <p className={`login-message is-${messageType}`}>{message}</p>
        )}
        <p className="register-switch">
          Already registered? <Link to="/login">Log in</Link>
        </p>
      </div>
    </section>
  );
}
