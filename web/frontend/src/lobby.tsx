import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./lobby.css";

type Table = {
  id: string;
  name: string;
  players: number;
  maxPlayers: number;
};

const INITIAL_TABLES: Table[] = [
  { id: "table-alpha", name: "Table Alpha", players: 2, maxPlayers: 5 },
  { id: "table-beta", name: "Table Beta", players: 3, maxPlayers: 5 },
  { id: "table-gamma", name: "Table Gamma", players: 1, maxPlayers: 5 },
];

export default function Lobby() {
  const navigate = useNavigate();
  const [tables, setTables] = useState<Table[]>(INITIAL_TABLES);
  const [newTableName, setNewTableName] = useState("");
  const [message, setMessage] = useState("");

  function joinTable(table: Table) {
    navigate(`/waiting/${table.id}`, { state: { tableName: table.name } });
  }

  function createTable(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = newTableName.trim();
    if (!trimmed) {
      setMessage("Please enter a table name.");
      return;
    }

    setMessage("");
    const createdTable: Table = {
      id: `table-${Date.now()}`,
      name: trimmed,
      players: 1,
      maxPlayers: 5,
    };

    setTables((current) => [createdTable, ...current]);
    setNewTableName("");
    navigate(`/waiting/${createdTable.id}`, {
      state: { tableName: createdTable.name },
    });
  }

  return (
    <section className="lobby-page">
      <div className="lobby-header">
        <h2>Lobby</h2>
        <p>Choose a table card to join, or create a new table.</p>
      </div>

      <form className="lobby-create" onSubmit={createTable}>
        <input
          type="text"
          placeholder="New table name"
          value={newTableName}
          onChange={(event) => {
            setNewTableName(event.target.value);
            if (message) {
              setMessage("");
            }
          }}
        />
        <button type="submit">Create Table</button>
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
            <h3>{table.name}</h3>
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
