import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { LOBBY_DETAIL_COMMAND } from "../network/commandTypes";
import {
  ERROR_EVENT,
  LOBBY_DETAIL_EVENT,
  MATCH_FOUND_EVENT,
} from "../network/eventTypes";
import { getEventData, wsClient } from "../network/wsClient";
import "./waiting.css";

type LobbyDetailEvent = {
  lobbyId: string;
  name: string;
  maxUser: number;
  numUser: number;
  currentUsers: string[];
  status: "WAITING";
};

type MatchFoundEvent = {
  game_id: string;
  host: string;
  port: number;
};

type ErrorEvent = {
  message?: string;
};

export default function Waiting() {
  const navigate = useNavigate();
  const { tableId, tableSize: tableSizeParam } = useParams();
  const parsedTableSize = Number(tableSizeParam);
  const [currentUsers, setCurrentUsers] = useState<string[]>([]);
  const [numUser, setNumUser] = useState(0);
  const [maxUser, setMaxUser] = useState(parsedTableSize);
  const [status, setStatus] = useState("Waiting for players...");
  const [message, setMessage] = useState("");
  const progressPercent =
    maxUser > 0 ? Math.round((numUser / maxUser) * 100) : 0;

  useEffect(() => {
    const playerId = localStorage.getItem("hanabi.playerId");
    const playerName = localStorage.getItem("hanabi.username") || playerId;

    if (!tableId) {
      navigate("/lobby");
      return;
    }

    if (!playerName) {
      navigate("/login");
      return;
    }

    const lobbyId = tableId;
    const currentPlayerName = playerName;
    let isMounted = true;

    async function loadLobbyDetail() {
      try {
        const events = await wsClient.command<{
          lobbyId: string;
          playerName: string;
        }>(
          LOBBY_DETAIL_COMMAND,
          { lobbyId, playerName: currentPlayerName },
        );

        const match = getEventData<MatchFoundEvent>(events, MATCH_FOUND_EVENT);
        if (match) {
          localStorage.setItem(
            "hanabi.gameWsUrl",
            `ws://${match.host}:${match.port}/ws`,
          );
          navigate(`/game/${match.game_id}`);
          return;
        }

        const detail = getEventData<LobbyDetailEvent>(events, LOBBY_DETAIL_EVENT);
        if (detail && isMounted) {
          setCurrentUsers(detail.currentUsers);
          setNumUser(detail.numUser);
          setMaxUser(detail.maxUser);
          setStatus(
            detail.numUser >= detail.maxUser
              ? "Preparing game..."
              : "Waiting for players...",
          );
          setMessage("");
          return;
        }

        const error = getEventData<ErrorEvent>(events, ERROR_EVENT);
        if (error && isMounted) {
          setMessage(error.message || "Unable to load lobby.");
        }
      } catch (error) {
        if (isMounted) {
          setMessage(error instanceof Error ? error.message : "Unable to load lobby.");
        }
      }
    }

    void loadLobbyDetail();
    const timer = window.setInterval(loadLobbyDetail, 1000);

    return () => {
      isMounted = false;
      window.clearInterval(timer);
    };
  }, [navigate, tableId]);

  return (
    <section className="waiting-page">
      <div className="waiting-card">
        <h2>Waiting for Players</h2>
        <p className="waiting-table-label">
          <strong>{tableId ?? "table"}</strong>
        </p>

        <div className="waiting-progress">
          <div className="waiting-progress-meta">
            <span>Players joined</span>
            <span>
              {numUser}/{maxUser}
            </span>
          </div>
          <div className="waiting-progress-track">
            <div
              className="waiting-progress-fill"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        <p className="waiting-status is-pending">
          {message || status}
        </p>

        <div className="waiting-users">
          {currentUsers.map((player) => (
            <span key={player}>{player}</span>
          ))}
        </div>
      </div>
    </section>
  );
}
