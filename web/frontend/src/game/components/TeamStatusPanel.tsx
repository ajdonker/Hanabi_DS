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
        <div className="token-reserve" aria-label="Reserve clue tokens">
          {Array.from({ length: reserveHints }).map((_, idx) => (
            <span key={idx} className="clue-token" />
          ))}
        </div>
        <div className="token-clues" aria-label="Available clue tokens">
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
