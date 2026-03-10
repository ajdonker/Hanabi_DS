type FireworksPanelProps = {
  colors: string[];
  values: number[];
};

export default function FireworksPanel({ colors, values }: FireworksPanelProps) {
  return (
    <section className="fireworks-panel">
      <div className="firework-lanes">
        {colors.map((color, index) => (
          <article
            key={color}
            className={`firework-lane ${color.toLowerCase()}`}
            aria-label={color}
            title={color}
          >
            <strong>{values[index] ?? 0}</strong>
          </article>
        ))}
      </div>
    </section>
  );
}
