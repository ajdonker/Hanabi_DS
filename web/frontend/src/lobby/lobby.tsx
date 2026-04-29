import { type FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  LOBBY_CREATE_COMMAND,
  LOBBY_JOIN_COMMAND,
  LOBBY_LIST_COMMAND,
} from "../network/commandTypes";
import {
  LOBBY_CREATED_EVENT,
  LOBBY_LIST_EVENT,
  MATCH_FOUND_EVENT,
  WAITING_EVENT,
} from "../network/eventTypes";
import { getEventData, wsClient } from "../network/wsClient";
import "./lobby.css";

type LobbyWire = {
  lobbyId: string;
  name: string;
  maxUser: number;
  numUser: number;
  currentUsers: string[];
};

type Table = LobbyWire;

type LobbyListEvent = {
  lobbies: LobbyWire[];
};

type MatchFoundEvent = {
  game_id: string;
  host: string;
  port: number;
};

export default function Lobby() {
  const navigate = useNavigate();
  const [tables, setTables] = useState<Table[]>([]);
  const [playerCountInput, setPlayerCountInput] = useState("2");
  const [message, setMessage] = useState("");
  const [isLoadingTables, setIsLoadingTables] = useState(true);
  const [isCreatingTable, setIsCreatingTable] = useState(false);
  const [joiningLobbyId, setJoiningLobbyId] = useState<string | null>(null);

  function generateLobbyId(): string {
    return `table-${crypto.randomUUID().slice(0, 8)}`;
  }

  useEffect(() => {
    let isMounted = true;

    async function loadLobbies() {
      try {
        setIsLoadingTables(true);
        const events = await wsClient.command<Record<string, never>>(
          LOBBY_LIST_COMMAND,
          {},
        );
        const payload = getEventData<LobbyListEvent>(events, LOBBY_LIST_EVENT);
        if (!payload) {
          throw new Error("Unable to parse lobby list.");
        }
        if (isMounted) {
          setTables(payload.lobbies);
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
    const username = localStorage.getItem("hanabi.username") || playerId;
    const isCurrentUserInLobby = table.currentUsers.includes(username);
    const isLobbyFull = table.numUser >= table.maxUser;

    if (isLobbyFull) {
      navigate(`/game/${table.lobbyId}`);
      return;
    }

    if (isCurrentUserInLobby) {
      navigate(`/waiting/${table.lobbyId}/${table.maxUser}`);
      return;
    }

    try {
      setMessage("");
      setJoiningLobbyId(table.lobbyId);
      const events = await wsClient.command<{ lobbyId: string; userJoined: string }>(
        LOBBY_JOIN_COMMAND,
        { lobbyId: table.lobbyId, userJoined: username },
      );

      const match = getEventData<MatchFoundEvent>(events, MATCH_FOUND_EVENT);
      if (match) {
        localStorage.setItem("hanabi.gameId", match.game_id);
        localStorage.setItem(
          "hanabi.gameWsUrl",
          `ws://${match.host}:${match.port}/ws`,
        );
        navigate(`/game/${match.game_id}`);
        return;
      }

      const waiting = getEventData<Record<string, never>>(events, WAITING_EVENT);
      if (!waiting) {
        const errorMsg = getEventData<{ message: string }>(events, "error");
        setMessage(errorMsg ? errorMsg.message : "Unknown error joining lobby.");
        return;
      }

      navigate(`/waiting/${table.lobbyId}/${table.maxUser}`);
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
      requestedPlayers > 4
    ) {
      setMessage("Please enter a valid number of players between 2 and 4.");
      return;
    }
    if (!playerId) {
      setMessage("Please login before creating a lobby.");
      navigate("/login");
      return;
    }
    const username = localStorage.getItem("hanabi.username") || playerId;
    if (isCreatingTable) {
      return;
    }

    try {
      setIsCreatingTable(true);
      setMessage("");
      const lobbyId = generateLobbyId();
      const events = await wsClient.command<{
        lobbyId: string;
        maxUsers: number;
        userCreator: string;
      }>(
        LOBBY_CREATE_COMMAND,
        { lobbyId, maxUsers: requestedPlayers, userCreator: username },
      );
      const created = getEventData<LobbyWire>(events, LOBBY_CREATED_EVENT);
      if (!created) {
        throw new Error("Create lobby failed: missing lobby_created event.");
      }

      setTables((current) => {
        const withoutCreated = current.filter((table) => table.lobbyId !== created.lobbyId);
        return [created, ...withoutCreated];
      });
      navigate(`/waiting/${created.lobbyId}/${created.maxUser}`);
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
            key={table.lobbyId}
            className="lobby-card"
            type="button"
            disabled={joiningLobbyId === table.lobbyId}
            onClick={() => joinTable(table)}
          >
            <h3>GameId: {table.lobbyId.replace("table-", "")}</h3>
            <p>
              Players: {table.numUser}/{table.maxUser}
            </p>
            <span>{joiningLobbyId === table.lobbyId ? "JOINING..." : "JOIN"}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
