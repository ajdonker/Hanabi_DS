type FireworksPanelProps = {
  colors: string[];
  values: number[];
  misfires: number;
  maxMisfires?: number;
};

export default function FireworksPanel({
  colors,
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
            title={color}
          >
            <strong>{values[index] ?? 0}</strong>
          </article>
        ))}
      </div>
      <div className="fireworks-misfires">
        {misfires}/{maxMisfires} misfires
      </div>
    </section>
  );
}
