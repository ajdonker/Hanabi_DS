import type { Player } from "../types";
import type { CardColor, CardValue } from "../types";
import Card from "./Card";

type PlayerHandProps = {
  player: Player;
  isCurrentPlayer?: boolean;
  orientation?: "horizontal" | "vertical";
  className?: string;
  cardRotationDeg?: number;
  numberRotationDeg?: number;
  nameSide?: "top" | "left" | "right";
  nameRotationDeg?: number;
  hoverShift?: "up" | "down" | "left" | "right" | "none";
};

const CARD_COLORS: CardColor[] = ["Red", "White", "Yellow", "Green", "Blue"];

function getDemoCard(playerId: number, cardIndex: number): {
  color: CardColor;
  value: CardValue;
} {
  const color = CARD_COLORS[(playerId + cardIndex) % CARD_COLORS.length];
  const value = (((playerId + cardIndex) % 5) + 1) as CardValue;

  return { color, value };
}

export default function PlayerHand({
  player,
  isCurrentPlayer = false,
  orientation = "horizontal",
  className = "",
  cardRotationDeg = 0,
  numberRotationDeg,
  nameSide = "top",
  nameRotationDeg = 0,
  hoverShift = "none",
}: PlayerHandProps) {
  const handClasses = `player-hand ${orientation} ${className}`.trim();
  const playerLabel = isCurrentPlayer ? "You" : player.name;
  const nameStyle =
    nameRotationDeg !== 0 ? { transform: `rotate(${nameRotationDeg}deg)` } : undefined;
  const effectiveCardRotation = isCurrentPlayer ? 0 : cardRotationDeg;
  const effectiveNumberRotation = numberRotationDeg ?? -effectiveCardRotation;

  const cards = (
    <div className="hand-cards">
      {Array.from({ length: 5 }).map((_, idx) => {
        const demoCard = getDemoCard(player.id, idx);

        return (
          <div key={idx} className={`card-hover-wrap hover-${hoverShift}`.trim()}>
            <Card
              color={demoCard.color}
              value={demoCard.value}
              faceDown={isCurrentPlayer}
              rotationDeg={effectiveCardRotation}
              numberRotationDeg={effectiveNumberRotation}
            />
          </div>
        );
      })}
    </div>
  );

  return (
    <article className={`${handClasses} name-${nameSide}`.trim()}>
      {nameSide === "top" ? (
        <>
          <h3 className="player-name top" style={nameStyle}>
            {playerLabel}
          </h3>
          {cards}
        </>
      ) : (
        <div className={`player-hand-main ${nameSide}`.trim()}>
          {nameSide === "left" && (
            <h3 className="player-name side" style={nameStyle}>
              {playerLabel}
            </h3>
          )}
          {cards}
          {nameSide === "right" && (
            <h3 className="player-name side" style={nameStyle}>
              {playerLabel}
            </h3>
          )}
        </div>
      )}
    </article>
  );
}
