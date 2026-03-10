import { useLocation, useParams } from "react-router-dom";
import "./game.css";
import ActionBar from "./components/ActionBar";
import DiscardPanel from "./components/DiscardPanel";
import FireworksPanel from "./components/FireworksPanel";
import GameHeader from "./components/GameHeader";
import PlayerHand from "./components/PlayerHand";
import TeamStatusPanel from "./components/TeamStatusPanel";
import type { DiscardTableData, Player } from "./types";

type GameState = {
  tableSize?: number;
};

function getImpression(score: number): string {
  if (score <= 5) {
    return "Horrible";
  }
  if (score <= 10) {
    return "Mediocre";
  }
  if (score <= 15) {
    return "Honorable";
  }
  if (score <= 20) {
    return "Excellent";
  }
  if (score <= 24) {
    return "Amazing";
  }
  return "Legendary";
}

export default function Game() {
  const { tableId } = useParams();
  const location = useLocation();
  const state = location.state as GameState | null;
  const tableSize = state?.tableSize ?? 4;
  const colors = ["Red", "Blue", "Green", "Yellow", "White"];
  const players: Player[] = Array.from({ length: tableSize }, (_, index) => ({
    id: index + 1,
    name: `Player ${index + 1}`,
  }));
  const safeTableId = tableId ?? "";
  const fireworkValues = [2, 1, 3, 0, 0];
  const teamScore = fireworkValues.reduce((sum, value) => sum + value, 0);
  const hints = 6;
  const fuses = 2;
  const deckCount = 34;
  const discardByColor: DiscardTableData = {
    Green: { ones: 2, twos: 1, threes: 0 },
    White: { ones: 1, twos: 2, threes: 1 },
    Red: { ones: 0, twos: 1, threes: 1 },
    Blue: { ones: 2, twos: 0, threes: 2 },
    Yellow: { ones: 1, twos: 1, threes: 0 },
  };
  const currentPlayer = players[0] ?? { id: 0, name: "Player 1" };
  const leftPlayer = players[1] ?? { id: 101, name: "Seat Left" };
  const topPlayer = players[2] ?? { id: 102, name: "Seat Top" };
  const rightPlayer = players[3] ?? { id: 103, name: "Seat Right" };

  return (
    <section className="game-page">
      <GameHeader tableId={safeTableId} tableSize={tableSize} />

      <div className="game-table">
        <PlayerHand
          player={leftPlayer}
          orientation="vertical"
          className="seat-left"
        />
        <PlayerHand player={topPlayer} orientation="horizontal" className="seat-top" />
        <PlayerHand
          player={rightPlayer}
          orientation="vertical"
          className="seat-right"
        />

        <main className="center-zone">
          <FireworksPanel colors={colors} values={fireworkValues} />
        </main>

        <PlayerHand
          player={currentPlayer}
          isCurrentPlayer
          orientation="horizontal"
          className="seat-bottom"
        />
        <DiscardPanel className="discard-bottom-left" discardByColor={discardByColor} />

        <TeamStatusPanel
          teamScore={teamScore}
          maxScore={25}
          hints={hints}
          maxHints={8}
          fuses={fuses}
          maxFuses={3}
          deckCount={deckCount}
          impression={getImpression(teamScore)}
        />
      </div>

      <ActionBar />
    </section>
  );
}
