import type { KeyboardEvent, MouseEvent } from "react";
import type { HandCard, Player } from "../types";
import type { CardColor, CardValue } from "../types";
import type { CardHintMarkers } from "../types";
import Card from "./Card";

export type CardSelectPayload = {
  color: CardColor;
  value: CardValue;
  sameColorCount: number;
  sameValueCount: number;
  popupPlacement: "auto" | "right" | "left";
  player: Player;
  cardIndex: number;
  anchorRect: DOMRect;
};

type PlayerHandProps = {
  player: Player;
  handCards: HandCard[];
  isCurrentPlayer?: boolean;
  orientation?: "horizontal" | "vertical";
  className?: string;
  cardRotationDeg?: number;
  numberRotationDeg?: number;
  nameSide?: "top" | "bottom" | "left" | "right";
  nameRotationDeg?: number;
  hoverShift?: "up" | "down" | "left" | "right" | "none";
  popupPlacement?: "auto" | "right-of-card" | "left-of-card";
  hintPosition?: "top" | "bottom" | "left" | "right";
  cardHintsByCard?: Record<number, CardHintMarkers>;
  onCardSelect?: (payload: CardSelectPayload) => void;
};

export default function PlayerHand({
  player,
  handCards,
  isCurrentPlayer = false,
  orientation = "horizontal",
  className = "",
  cardRotationDeg = 0,
  numberRotationDeg,
  nameSide = "top",
  nameRotationDeg = 0,
  hoverShift = "none",
  popupPlacement = "auto",
  hintPosition = "top",
  cardHintsByCard,
  onCardSelect,
}: PlayerHandProps) {
  const handClasses = `player-hand ${orientation} ${className}`.trim();
  const playerLabel = isCurrentPlayer ? "You" : player.name;
  const nameColorClass = isCurrentPlayer ? "you" : `player-${player.id}`;
  const nameStyle = 
    (nameSide === "left" || nameSide === "right") && nameRotationDeg !== 0
      ? { transform: `rotate(${nameRotationDeg}deg)` }
      : undefined;
    
  const effectiveCardRotation = isCurrentPlayer ? 0 : cardRotationDeg;
  const effectiveNumberRotation = numberRotationDeg ?? -effectiveCardRotation;
  const cardsData = handCards;

  const renderedCards = (
    <div className="hand-cards">
      {cardsData.map((demoCard, idx) => {
        const cardHints = cardHintsByCard?.[idx];
        const hasCardHint = Boolean(cardHints?.numberHint || cardHints?.colorHint);
        const hintColorClass = cardHints?.colorHint
          ? `hint-${cardHints.colorHint.toLowerCase()}`
          : "hint-neutral";
        const canSelectCard = Boolean(onCardSelect);
        const sameColorCount = cardsData.filter((card) => card.color === demoCard.color).length;
        const sameValueCount = cardsData.filter((card) => card.value === demoCard.value).length;
        const handleSelect = (anchorRect: DOMRect) => {
          if (!onCardSelect) {
            return;
          }

          onCardSelect({
            color: demoCard.color,
            value: demoCard.value,
            sameColorCount,
            sameValueCount,
            popupPlacement:
              popupPlacement === "right-of-card"
                ? "right"
                : popupPlacement === "left-of-card"
                  ? "left"
                  : "auto",
            player,
            cardIndex: idx,
            anchorRect,
          });
        };
        const getStableAnchorRect = (element: HTMLDivElement): DOMRect => {
          const rect = element.getBoundingClientRect();
          const transform = window.getComputedStyle(element).transform;

          if (!transform || transform === "none") {
            return rect;
          }

          let tx = 0;
          let ty = 0;
          const matrixMatch = transform.match(/matrix\(([^)]+)\)/);
          const matrix3dMatch = transform.match(/matrix3d\(([^)]+)\)/);

          if (matrixMatch) {
            const values = matrixMatch[1]?.split(",").map((v) => Number(v.trim())) ?? [];
            tx = values[4] ?? 0;
            ty = values[5] ?? 0;
          } else if (matrix3dMatch) {
            const values = matrix3dMatch[1]?.split(",").map((v) => Number(v.trim())) ?? [];
            tx = values[12] ?? 0;
            ty = values[13] ?? 0;
          }

          return new DOMRect(rect.left - tx, rect.top - ty, rect.width, rect.height);
        };
        const handleCardClick = (event: MouseEvent<HTMLDivElement>) => {
          if (!canSelectCard) {
            return;
          }

          handleSelect(getStableAnchorRect(event.currentTarget));
        };

        return (
          <div
            key={idx}
            className={`card-hover-wrap hover-${hoverShift} ${
              canSelectCard ? "selectable-card" : ""
            }`.trim()}
            onClick={handleCardClick}
            tabIndex={canSelectCard ? 0 : undefined}
            data-hint-card={canSelectCard ? "true" : undefined}
          >
            {hasCardHint && (
              <div
                className={`card-hint-area hint-pos-${hintPosition} ${hintColorClass}`.trim()}
              >
                <span className="card-hint-value">{cardHints?.numberHint ?? ""}</span>
              </div>
            )}
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
      {nameSide === "top" || nameSide === "bottom" ? (
        <>
          {nameSide === "top" && (
            <h3 className={`player-name top ${nameColorClass}`.trim()} style={nameStyle}>
              {playerLabel}
            </h3>
          )}
          {renderedCards}
          {nameSide === "bottom" && (
            <h3 className={`player-name bottom ${nameColorClass}`.trim()} style={nameStyle}>
              {playerLabel}
            </h3>
          )}
        </>
      ) : (
        <div className={`player-hand-main ${nameSide}`.trim()}>
          {nameSide === "left" && (
            <h3 className={`player-name side side-left ${nameColorClass}`.trim()} style={nameStyle}>
              {playerLabel}
            </h3>
          )}
          {renderedCards}
          {nameSide === "right" && (
            <h3
              className={`player-name side side-right ${nameColorClass}`.trim()}
              style={nameStyle}
            >
              {playerLabel}
            </h3>
          )}
        </div>
      )}
    </article>
  );
}
