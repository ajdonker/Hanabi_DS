import { colors } from "../config";
import type { CardValue, FireworkValue } from "../types";
import Card from "./Card";
type FireworksPanelProps = {
  values: FireworkValue[];
  misfires: number;
  maxMisfires?: number;
};

export default function FireworksPanel({
  values,
  misfires,
  maxMisfires = 3,
}: FireworksPanelProps) {
  const isCardValue = (value: FireworkValue): value is CardValue => value > 0;
  
  return (
    <section className="fireworks-panel">
      <div className="firework-lanes">
        {colors.map((color, index) => {
          const value = values[index] ?? 0;

          return (
            <article
              key={color}
              className={`firework-lane ${color.toLowerCase()}`}
            >
              {isCardValue(value) && <Card
                color={color}
                value={value}
                rotationDeg={180}
                numberRotationDeg={180}
              />}
            </article>
          );
        })}
      </div>
      <div className="fireworks-misfires">
        {misfires}/{maxMisfires} misfires
      </div>
    </section>
  );
}
