import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import "./waiting.css";

type WaitingState = {
  tableSize?: number;
};

export default function Waiting() {
  const navigate = useNavigate();
  const { tableId } = useParams();
  const location = useLocation();
  const state = location.state as WaitingState | null;
  const tableSize = state?.tableSize ?? 4;
  const [acceptedPlayers, setAcceptedPlayers] = useState(0);
  const [status, setStatus] = useState("Click Accept when you are ready.");
  const [isAccepted, setIsAccepted] = useState(false);
  const progressPercent =
    tableSize > 0 ? Math.round((acceptedPlayers / tableSize) * 100) : 0;

  function handleAccept() {
    if (isAccepted) {
      return;
    }
    setIsAccepted(true);
    setAcceptedPlayers(1);
    setStatus("You accepted. Waiting for other players...");
  }

  function handleDecline() {
    setIsAccepted(false);
    setAcceptedPlayers(0);
    setStatus("You declined. Click Accept when you are ready.");
  }

  useEffect(() => {
    if (!isAccepted || acceptedPlayers >= tableSize) {
      return;
    }

    const timer = window.setInterval(() => {
      setAcceptedPlayers((current) => Math.min(tableSize, current + 1));
    }, 900);

    return () => window.clearInterval(timer);
  }, [isAccepted, acceptedPlayers, tableSize]);

  useEffect(() => {
    if (acceptedPlayers === tableSize) {
      navigate(`/game/${tableId ?? ""}`, { state: { tableSize } });
    }
  }, [acceptedPlayers, navigate, tableId, tableSize]);

  return (
    <section className="waiting-page">
      <div className="waiting-card">
        <h2>You are going to play Hanabi</h2>
        <p className="waiting-table-label">
          <strong>{tableId ?? "table"}</strong>
        </p>

        <div className="waiting-progress">
          <div className="waiting-progress-meta">
            <span>Accepted players</span>
            <span>
              {acceptedPlayers}/{tableSize}
            </span>
          </div>
          <div
            className="waiting-progress-track"
          >
            <div
              className="waiting-progress-fill"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        <p className={`waiting-status ${isAccepted ? "is-accepted" : "is-pending"}`}>
          {status}
        </p>

        <div className="waiting-actions">
          <button type="button" className="accept-button" onClick={handleAccept} disabled={isAccepted}>
            {isAccepted ? "Accepted" : "Accept"}
          </button>
          <button type="button" className="decline-button" onClick={handleDecline}>
            Decline
          </button>
        </div>
      </div>
    </section>
  );
}
