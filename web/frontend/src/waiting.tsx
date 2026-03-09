import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import "./waiting.css";

type WaitingState = {
  tableName?: string;
};

export default function Waiting() {
  const navigate = useNavigate();
  const { tableId } = useParams();
  const location = useLocation();
  const state = location.state as WaitingState | null;
  const tableName = state?.tableName ?? `Table ${tableId ?? ""}`;
  const tableSize = 4;
  const [acceptedPlayers, setAcceptedPlayers] = useState(0);
  const [status, setStatus] = useState("Click Accept when you are ready.");
  const [isAccepted, setIsAccepted] = useState(false);

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
      navigate(`/game/${tableId ?? ""}`, { state: { tableName } });
    }
  }, [acceptedPlayers, navigate, tableId, tableName, tableSize]);

  return (
    <section className="waiting-page">
      <h2>Waiting Room</h2>
      <p>You joined: {tableName}</p>
      <p>Accepted players: {acceptedPlayers}/4</p>
      <p>{status}</p>
      <div className="waiting-actions">
        <button type="button" onClick={handleAccept}>
          Accept
        </button>
        <button type="button" onClick={handleDecline}>
          Decline
        </button>
      </div>
    </section>
  );
}
