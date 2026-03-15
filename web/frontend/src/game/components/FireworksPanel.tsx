type FireworksPanelProps = {
  values: number[];
  misfires: number;
  maxMisfires?: number;
};

export default function FireworksPanel({
  values,
  misfires,
  maxMisfires = 3,
}: FireworksPanelProps) {
  const colors = ["Red", "Blue", "Green", "Yellow", "White"];
  return (
    <section className="fireworks-panel">
      <div className="firework-lanes">
        {colors.map((color, index) => (
          <article
            key={color}
            className={`firework-lane ${color.toLowerCase()}`}
          >
            <strong>{values[index]}</strong>
          </article>
        ))}
      </div>
      <div className="fireworks-misfires">
        {misfires}/{maxMisfires} misfires
      </div>
    </section>
  );
}
