import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./lobby.css";

const CREATE_TABLE_API_ENDPOINT = "/api/hanabi/lobby/create";

type CreateTableResponse = {
  ok?: boolean;
  status?: string;
  result?: string;
  message?: string;
  tableId?: string;
  table_id?: string;
  id?: string;
  table?: {
    id?: string;
    tableId?: string;
    table_id?: string;
  };
};

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
  const [playerCountInput, setPlayerCountInput] = useState("2");
  const [message, setMessage] = useState("");
  const [isCreatingTable, setIsCreatingTable] = useState(false);

  function joinTable(table: Table) {
    navigate(`/waiting/${table.id}`, { state: { tableSize: table.maxPlayers } });
  }

  async function createTable(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const requestedPlayers = Number(playerCountInput);

    if (
      !Number.isInteger(requestedPlayers) ||
      requestedPlayers < 2 ||
      requestedPlayers > 4
    ) {
      setMessage("Please enter a valid number of players between 2 and 4.");
      return;
    }
    if (isCreatingTable) {
      return;
    }

    try {
      setIsCreatingTable(true);
      setMessage("");

      const response = await fetch(CREATE_TABLE_API_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          playerCountInput,
          playerCount: requestedPlayers,
        }),
      });

      if (!response.ok) {
        setMessage("Create game failed. Please try again.");
        return;
      }

      let isBackendOk = false;
      const contentType = response.headers.get("content-type") ?? "";

      if (contentType.includes("application/json")) {
        const data = (await response.json()) as CreateTableResponse;
        const status = (data.status ?? data.result ?? data.message ?? "").trim().toUpperCase();
        isBackendOk = data.ok === true || status === "OK";
      } else {
        const text = (await response.text()).trim().toUpperCase();
        isBackendOk = text === "OK";
      }

      if (!isBackendOk) {
        setMessage("Create game was rejected by backend.");
        return;
      }

      const createdTable: Table = {
        id: 'todo', // In a real implementation, this would come from the backend response
        players: 1,
        maxPlayers: requestedPlayers,
      };

      setTables((current) => [createdTable, ...current]);
      navigate(`/waiting/todo`, {
        state: { tableSize: requestedPlayers },
      });
    } catch (error) {
      console.error("Failed to create table:", error);
      setMessage("Unable to reach backend.");
    } finally {
      setIsCreatingTable(false);
    }
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
          placeholder="Number of players"
          value={playerCountInput}
          onChange={(event) => {
            setPlayerCountInput(event.target.value);
            if (message) {
              setMessage("");
            }
          }}
        />
        <button type="submit" disabled={isCreatingTable}>
          {isCreatingTable ? "Creating..." : "Create Game"}
        </button>
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
            <span>JOIN</span>
          </button>
        ))}
      </div>
    </section>
  );
}
