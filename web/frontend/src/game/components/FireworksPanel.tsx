import { colors } from "../config";
import type { CardValue } from "../types";
import Card from "./Card";
type FireworksPanelProps = {
  values: CardValue[];
  misfires: number;
  maxMisfires?: number;
};

export default function FireworksPanel({
  values,
  misfires,
  maxMisfires = 3,
}: FireworksPanelProps) {
  
  return (
    <section className="fireworks-panel">
      <div className="firework-lanes">
        {colors.map((color, index) => (
          <article
            key={color}
            className={`firework-lane ${color.toLowerCase()}`}
          >
            {values[index] > 0 && <Card
              color={color}
              value={values[index]}
              rotationDeg={180}
              numberRotationDeg={180}
            />}
          </article>
        ))}
      </div>
      <div className="fireworks-misfires">
        {misfires}/{maxMisfires} misfires
      </div>
    </section>
  );
}
