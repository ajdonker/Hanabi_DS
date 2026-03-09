import { useLocation, useParams } from "react-router-dom";

type GameState = {
  tableName?: string;
};

export default function Game() {
  const { tableId } = useParams();
  const location = useLocation();
  const state = location.state as GameState | null;
  const tableName = state?.tableName ?? `Table ${tableId ?? ""}`;

  return (
    <section>
      <h2>Game Page</h2>
      <p>Game started for {tableName}.</p>
    </section>
  );
}
