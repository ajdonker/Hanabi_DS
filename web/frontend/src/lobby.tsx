import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./lobby.css";

type Table = {
  id: string;
  players: number;
  maxPlayers: number;
};

const INITIAL_TABLES: Table[] = [
  { id: "table-alpha", players: 2, maxPlayers: 4 },
  { id: "table-beta", players: 3, maxPlayers: 5 },
  { id: "table-gamma", players: 1, maxPlayers: 2 },
];

export default function Lobby() {
  const navigate = useNavigate();
  const [tables, setTables] = useState<Table[]>(INITIAL_TABLES);
  const [playerCountInput, setPlayerCountInput] = useState("4");
  const [message, setMessage] = useState("");

  function joinTable(table: Table) {
    navigate(`/waiting/${table.id}`, { state: { tableSize: table.maxPlayers } });
  }

  function createTable(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const requestedPlayers = Number(playerCountInput);

    if (!Number.isInteger(requestedPlayers) || requestedPlayers < 2) {
      setMessage("Please enter a valid number of players (minimum 2).");
      return;
    }

    setMessage("");
    const createdTable: Table = {
      id: `table-${Date.now()}`,
      players: 1,
      maxPlayers: requestedPlayers,
    };

    setTables((current) => [createdTable, ...current]);
    setPlayerCountInput("4");
    navigate(`/waiting/${createdTable.id}`, {
      state: { tableSize: createdTable.maxPlayers },
    });
  }

  return (
    <section className="lobby-page">
      <div className="lobby-header">
        <h2>Lobby</h2>
        <p>Choose a game card to join, or create a new game.</p>
      </div>

      <form className="lobby-create" onSubmit={createTable}>
        <input
          type="number"
          min={2}
          placeholder="Number of players"
          value={playerCountInput}
          onChange={(event) => {
            setPlayerCountInput(event.target.value);
            if (message) {
              setMessage("");
            }
          }}
        />
        <button type="submit">Create Game</button>
      </form>
      {message && <p className="lobby-message">{message}</p>}

      <div className="lobby-grid">
        {tables.map((table) => (
          <button
            key={table.id}
            className="lobby-card"
            type="button"
            onClick={() => joinTable(table)}
          >
            <h3>Game {table.id.replace("table-", "")}</h3>
            <p>
              Players: {table.players}/{table.maxPlayers}
            </p>
            <span>Click to join</span>
          </button>
        ))}
      </div>
    </section>
  );
}
