import { useLocation } from "react-router-dom";
import "./game.css";
import ActionBar from "./components/ActionBar";
import Deckcount from "./components/Deckcount";
import DiscardPanel from "./components/DiscardPanel";
import FireworksPanel from "./components/FireworksPanel";
import GameHeader from "./components/GameHeader";
import PlayerHand from "./components/PlayerHand";
import TeamStatusPanel from "./components/TeamStatusPanel";
import type { DiscardTableData, Player } from "./types";

type GameState = {
  tableSize?: number;
};

export default function Game() {
  const location = useLocation();
  const state = location.state as GameState | null;
  const tableSize = state?.tableSize ?? 4;
  const colors = ["Red", "Blue", "Green", "Yellow", "White"];
  const players: Player[] = Array.from({ length: tableSize }, (_, index) => ({
    id: index + 1,
    name: `Player ${index + 1}`,
  }));
  const fireworkValues = [2, 1, 3, 0, 0];
  const hints = 4;
  const misfires = 2;
  const deckCount = 34;
  const discardByColor: DiscardTableData = {
    Green: { 1: 2, 2: 1, 3: 0, 4: 0, 5: 0 },
    White: { 1: 1, 2: 2, 3: 1, 4: 0, 5: 0 },
    Red: { 1: 0, 2: 1, 3: 1, 4: 1, 5: 0 },
    Blue: { 1: 2, 2: 0, 3: 2, 4: 0, 5: 1 },
    Yellow: { 1: 1, 2: 1, 3: 0, 4: 1, 5: 0 },
  };
  const currentPlayer = players[0] ?? { id: 1, name: "Player 1" };
  let topPlayer: Player | undefined;
  let leftPlayer: Player | undefined;
  let rightPlayer: Player | undefined;

  if (tableSize <= 2) {
    topPlayer = players[1];
  } else if (tableSize === 3) {
    topPlayer = players[1];
    leftPlayer = players[2];
  } else {
    leftPlayer = players[1];
    topPlayer = players[2];
    rightPlayer = players[3];
  }

  const activePlayer = topPlayer?.name ?? currentPlayer.name;
  const tableClass = tableSize <= 2 ? "players-2" : tableSize === 3 ? "players-3" : "players-4";

  return (
    <section className="game-page">
      <GameHeader activePlayer={activePlayer} />

      <div className={`game-table ${tableClass}`.trim()}>
        {leftPlayer && (
          <PlayerHand
            player={leftPlayer}
            orientation="vertical"
            cardRotationDeg={-90}
            nameSide="right"
            nameRotationDeg={90}
            hoverShift="right"
            className="seat-left"
          />
        )}
        {topPlayer && (
          <PlayerHand
            player={topPlayer}
            orientation="horizontal"
            hoverShift="down"
            className="seat-top"
          />
        )}
        {rightPlayer && (
          <PlayerHand
            player={rightPlayer}
            orientation="vertical"
            cardRotationDeg={90}
            nameSide="left"
            nameRotationDeg={-90}
            hoverShift="left"
            className="seat-right"
          />
        )}

        <main className="center-zone">
          <Deckcount deckCount={deckCount} />
          <FireworksPanel colors={colors} values={fireworkValues} misfires={misfires} />
        </main>

        <PlayerHand
          player={currentPlayer}
          isCurrentPlayer
          orientation="horizontal"
          hoverShift="up"
          className="seat-bottom"
        />
        <DiscardPanel className="discard-bottom-left" discardByColor={discardByColor} />

        <TeamStatusPanel hints={hints} />
      </div>

      <ActionBar />
    </section>
  );
}
