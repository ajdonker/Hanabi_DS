import type { Player } from "../types";

type PlayerHandProps = {
  player: Player;
  isCurrentPlayer?: boolean;
  orientation?: "horizontal" | "vertical";
  className?: string;
};

export default function PlayerHand({
  player,
  isCurrentPlayer = false,
  orientation = "horizontal",
  className = "",
}: PlayerHandProps) {
  const handClasses = `player-hand ${orientation} ${className}`.trim();

  return (
    <article className={handClasses}>
      <h3 className="player-name">{isCurrentPlayer ? "You" : player.name}</h3>
      <div className="hand-cards">
        {Array.from({ length: 5 }).map((_, idx) =>
          isCurrentPlayer ? (
            <button key={idx} className="card-face" type="button">
              ?
            </button>
          ) : (
            <div key={idx} className="card-back" />
          ),
        )}
      </div>
    </article>
  );
}
