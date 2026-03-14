import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./login.css";

const LOGIN_API_ENDPOINT = "/api/hanabi/login";

type LoginResponse = {
  ok?: boolean;
  status?: string;
  result?: string;
  message?: string;
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

      const response = await fetch(LOGIN_API_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: trimmed }),
      });

      if (!response.ok) {
        setMessage("Login failed. Please try again.");
        return;
      }

      const contentType = response.headers.get("content-type") ?? "";
      let isBackendOk = false;

      if (contentType.includes("application/json")) {
        const data = (await response.json()) as LoginResponse;
        const status = (data.status ?? data.result ?? data.message ?? "").trim().toUpperCase();
        isBackendOk = data.ok === true || status === "OK";
      } else {
        const text = (await response.text()).trim().toUpperCase();
        isBackendOk = text === "OK";
      }

      if (isBackendOk) {
        navigate("/lobby");
        return;
      }

      setMessage("Login was rejected by backend.");
    } catch (error) {
      console.error("Failed to submit login:", error);
      setMessage("Unable to reach backend.");
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
