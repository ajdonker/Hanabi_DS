import { FormEvent, useState } from "react";
import "./login.css";

export default function Login() {
  const [username, setUsername] = useState("");
  const [message, setMessage] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = username.trim();
    setMessage(trimmed ? `Welcome, ${trimmed}!` : "Please enter a username.");
  }

  return (
    <section className="login-page">
      <div className="login-card">
        <h2>Login</h2>
        <p className="login-subtitle">Sign in to continue to Hanabi.</p>
        <form className="login-form" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Enter username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />
          <button type="submit">Login</button>
        </form>
        {message && <p className="login-message">{message}</p>}
      </div>
    </section>
  );
}
