type TeamStatusPanelProps = {
  hints: number;
};

export default function TeamStatusPanel({ hints }: TeamStatusPanelProps) {
  const maxHints = 8;
  const visibleHints = Math.max(0, Math.min(maxHints, hints));
  const reserveHints = Math.max(0, maxHints - visibleHints);

  return (
    <aside className="team-status-panel">
      <div className="token-board">
        <div className="token-reserve">
          {Array.from({ length: reserveHints }).map((_, idx) => (
            <span key={idx} className="clue-token" />
          ))}
        </div>
        <div className="token-clues">
          <div className="clue-grid">
            {Array.from({ length: visibleHints }).map((_, idx) => (
              <span key={idx} className="clue-token">
                {idx === visibleHints - 1 && visibleHints > 0 && (
                  <strong className="clue-count">{visibleHints}</strong>
                )}
              </span>
            ))}
          </div>
        </div>
      </div>
    </aside>
  );
}
