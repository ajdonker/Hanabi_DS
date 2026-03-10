type FireworksPanelProps = {
  colors: string[];
  values: number[];
};

export default function FireworksPanel({ colors, values }: FireworksPanelProps) {
  return (
    <section className="fireworks-panel">
      <h3>Fireworks</h3>
      <div className="firework-lanes">
        {colors.map((color, index) => (
          <article key={color} className={`firework-lane ${color.toLowerCase()}`}>
            <span>{color}</span>
            <strong>{values[index] ?? 0}</strong>
          </article>
        ))}
      </div>
    </section>
  );
}
