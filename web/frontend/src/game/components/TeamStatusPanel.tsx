type TeamStatusPanelProps = {
  teamScore: number;
  maxScore: number;
  hints: number;
  maxHints: number;
  fuses: number;
  maxFuses: number;
  deckCount: number;
  impression: string;
};

export default function TeamStatusPanel({
  teamScore,
  maxScore,
  hints,
  maxHints,
  fuses,
  maxFuses,
  deckCount,
  impression,
}: TeamStatusPanelProps) {
  return (
    <aside className="team-status-panel">
      <h3>Team Status</h3>
      <div className="status-row">
        <span>Score</span>
        <strong>
          {teamScore}/{maxScore}
        </strong>
      </div>
      <div className="status-row">
        <span>Hints</span>
        <strong>
          {hints}/{maxHints}
        </strong>
      </div>
      <div className="status-row">
        <span>Misfires</span>
        <strong>
          {fuses}/{maxFuses}
        </strong>
      </div>
      <div className="status-row">
        <span>Deck</span>
        <strong>{deckCount}</strong>
      </div>
      <p className="status-impression">{impression}</p>
    </aside>
  );
}
