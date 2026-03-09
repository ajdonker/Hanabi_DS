import { Link, useLocation, useParams } from "react-router-dom";

type WaitingState = {
  tableName?: string;
};

export default function Waiting() {
  const { tableId } = useParams();
  const location = useLocation();
  const state = location.state as WaitingState | null;
  const tableName = state?.tableName ?? `Table ${tableId ?? ""}`;

  return (
    <section>
      <h2>Waiting Room</h2>
      <p>You joined: {tableName}</p>
      <p>Table ID: {tableId}</p>
      <p>Waiting for other players to join...</p>
      <p>
        <Link to="/lobby">Back to Lobby</Link>
      </p>
    </section>
  );
}
