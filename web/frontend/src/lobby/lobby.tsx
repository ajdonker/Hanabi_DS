import { type FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getEventData, wsClient } from "../network/wsClient";
import "./lobby.css";

type Table = {
  id: string;
  players: number;
  maxPlayers: number;
};

type LobbyWire = {
  lobbyId: string;
  name: string;
  maxUser: number;
  numUser: number;
  currentUsers: string[];
};

type LobbyListEvent = {
  lobbies: LobbyWire[];
};

export default function Lobby() {
  const navigate = useNavigate();
  const [tables, setTables] = useState<Table[]>([]);
  const [playerCountInput, setPlayerCountInput] = useState("2");
  const [message, setMessage] = useState("");
  const [isLoadingTables, setIsLoadingTables] = useState(true);
  const [isCreatingTable, setIsCreatingTable] = useState(false);
  const [joiningLobbyId, setJoiningLobbyId] = useState<string | null>(null);

  function toTable(lobby: LobbyWire): Table {
    return {
      id: lobby.lobbyId,
      players: lobby.numUser,
      maxPlayers: lobby.maxUser,
    };
  }

  useEffect(() => {
    let isMounted = true;

    async function loadLobbies() {
      try {
        setIsLoadingTables(true);
        const events = await wsClient.command<Record<string, never>>(
          "player.list_lobbies",
          {},
        );
        const payload = getEventData<LobbyListEvent>(events, "lobby_list");
        if (!payload) {
          throw new Error("Unable to parse lobby list.");
        }
        if (isMounted) {
          setTables(payload.lobbies.map(toTable));
        }
      } catch (error) {
        if (isMounted) {
          setMessage(error instanceof Error ? error.message : "Unable to load lobbies.");
        }
      } finally {
        if (isMounted) {
          setIsLoadingTables(false);
        }
      }
    }

    void loadLobbies();
    return () => {
      isMounted = false;
    };
  }, []);

  async function joinTable(table: Table) {
    const playerId = localStorage.getItem("hanabi.playerId");
    if (!playerId) {
      setMessage("Please login before joining a lobby.");
      navigate("/login");
      return;
    }

    try {
      setMessage("");
      setJoiningLobbyId(table.id);
      const events = await wsClient.command<{ playerId: string; lobbyId: string }>(
        "player.join_lobby",
        { playerId, lobbyId: table.id },
      );

      const joined = getEventData<LobbyWire>(events, "player_joined");
      navigate(`/waiting/${table.id}`, {
        state: { tableSize: joined?.maxUser ?? table.maxPlayers },
      });
    } catch (error) {
      console.error("Failed to join lobby:", error);
      setMessage(error instanceof Error ? error.message : "Unable to join lobby.");
    } finally {
      setJoiningLobbyId(null);
    }
  }

  async function createTable(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const requestedPlayers = Number(playerCountInput);
    const playerId = localStorage.getItem("hanabi.playerId");

    if (
      !Number.isInteger(requestedPlayers) ||
      requestedPlayers < 2 ||
      requestedPlayers > 5
    ) {
      setMessage("Please enter a valid number of players between 2 and 5.");
      return;
    }
    if (!playerId) {
      setMessage("Please login before creating a lobby.");
      navigate("/login");
      return;
    }
    if (isCreatingTable) {
      return;
    }

    try {
      setIsCreatingTable(true);
      setMessage("");
      const events = await wsClient.command<{ playerId: string; maxUser: number }>(
        "player.create_lobby",
        { playerId, maxUser: requestedPlayers },
      );
      const created = getEventData<LobbyWire>(events, "lobby_created");
      if (!created) {
        throw new Error("Create lobby failed: missing lobby_created event.");
      }
      const createdTable = toTable(created);

      setTables((current) => {
        const withoutCreated = current.filter((table) => table.id !== createdTable.id);
        return [createdTable, ...withoutCreated];
      });
      navigate(`/waiting/${createdTable.id}`, {
        state: { tableSize: createdTable.maxPlayers },
      });
    } catch (error) {
      console.error("Failed to create table:", error);
      setMessage(error instanceof Error ? error.message : "Unable to reach backend.");
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
        {isLoadingTables && <p>Loading lobbies...</p>}
        {!isLoadingTables && tables.length === 0 && <p>No lobbies available yet.</p>}
        {tables.map((table) => (
          <button
            key={table.id}
            className="lobby-card"
            type="button"
            disabled={joiningLobbyId === table.id}
            onClick={() => joinTable(table)}
          >
            <h3>Game {table.id.replace("table-", "")}</h3>
            <p>
              Players: {table.players}/{table.maxPlayers}
            </p>
            <span>{joiningLobbyId === table.id ? "JOINING..." : "JOIN"}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
