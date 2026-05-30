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
      className={`hanabi-card face-up card-${color.toLowerCase()} ${rotationDeg ? "rotated-card" : ""}`.trim()}
      style={baseStyle}
    >
      <div
        className={`card-number card-number-${color.toLowerCase()}`.trim()}
        style={{
          transform: numberRotationDeg ? `rotate(${numberRotationDeg}deg)` : undefined,
        }}
      >
        {value}
      </div>
    </div>
  );
}
