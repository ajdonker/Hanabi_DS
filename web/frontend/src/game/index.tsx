import { useLocation, useParams } from "react-router-dom";

type GameState = {
  tableSize?: number;
};

export default function Game() {
  const { tableId } = useParams();
  const location = useLocation();
  const state = location.state as GameState | null;
  const tableSize = state?.tableSize ?? 4;

  return (
    <section>
      <h2>Game Page</h2>
      <p>Game started for Table {tableId ?? ""}.</p>
      <p>Total players: {tableSize}</p>
    </section>
  );
}
