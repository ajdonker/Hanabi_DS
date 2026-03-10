import type { CSSProperties } from "react";
import type { CardColor, CardValue } from "../types";
import "./Card.css";

type CardProps = {
  color: CardColor;
  value: CardValue;
  faceDown?: boolean;
  rotationDeg?: number;
  numberRotationDeg?: number;
};

const COLOR_ROW_INDEX: Record<CardColor, number> = {
  Red: 0,
  Yellow: 1,
  Green: 2,
  Blue: 3,
  White: 4,
};

function toSpritePercent(index: number, maxIndex: number): string {
  return `${(index / maxIndex) * 100}%`;
}

export default function Card({
  color,
  value,
  faceDown = false,
  rotationDeg = 0,
  numberRotationDeg = 0,
}: CardProps) {
  const xPos = toSpritePercent(value - 1, 4);
  const yPos = toSpritePercent(COLOR_ROW_INDEX[color], 6);
  const baseStyle: CSSProperties = {
    transform: rotationDeg ? `rotate(${rotationDeg}deg)` : undefined,
  };

  if (faceDown) {
    return (
      <div
        className={`hanabi-card face-down ${rotationDeg ? "rotated-card" : ""}`.trim()}
        style={baseStyle}
      />
    );
  }

  return (
    <div
      className={`hanabi-card face-up ${rotationDeg ? "rotated-card" : ""}`.trim()}
      style={baseStyle}
    >
      <div
        className="card-section card-background"
        style={{ backgroundPosition: `${xPos} ${yPos}` }}
      />
      <div
        className="card-section card-number"
        style={{
          backgroundPosition: `${xPos} ${yPos}`,
          transform: numberRotationDeg ? `rotate(${numberRotationDeg}deg)` : undefined,
        }}
      />
    </div>
  );
}
