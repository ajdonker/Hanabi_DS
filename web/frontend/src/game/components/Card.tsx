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

const COLOR_SYMBOL: Record<CardColor, string> = {
  Red: "R",
  Yellow: "Y",
  Green: "G",
  Blue: "B",
  White: "W",
};

export default function Card({
  color,
  value,
  faceDown = false,
  rotationDeg = 0,
  numberRotationDeg = 0,
}: CardProps) {
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
      className={`hanabi-card face-up color-${color.toLowerCase()} ${rotationDeg ? "rotated-card" : ""}`.trim()}
      style={baseStyle}
    >
      <span className="card-corner card-corner-top">{value}</span>
      <span className="card-symbol" aria-hidden="true">{COLOR_SYMBOL[color]}</span>
      <span
        className="card-value"
        style={{
          transform: numberRotationDeg ? `rotate(${numberRotationDeg}deg)` : undefined,
        }}
      >
        {value}
      </span>
      <span className="card-corner card-corner-bottom">{value}</span>
    </div>
  );
}
