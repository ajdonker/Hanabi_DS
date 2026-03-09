import { useState } from "react";

export default function About() {
  const [username, setUsername] = useState("Alice");

  function changeUsername() {
    setUsername("Bob");
  }

  return (
    <div>
      <h2>About</h2>

      <div>Username: {username}</div>

      <button onClick={changeUsername}>Change Username</button>
      {username === "Bob" && (
        <div style={{ color: "green" }}>I love Bob</div>
      )}
    </div>
  );
}
