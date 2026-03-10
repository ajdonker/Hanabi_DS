import type { Player } from "../types";

type TeamStatusPanelProps = {
  teamScore: number;
  maxScore: number;
  hints: number;
  misfires: number;
  players: Player[];
};

export default function TeamStatusPanel({
  teamScore,
  maxScore,
  hints,
  misfires,
  players,
}: TeamStatusPanelProps) {
  return (
    <aside className="team-status-panel">
      <div className="token-board">
        <div className="hint-row">
          {Array.from({ length: 8 }).map((_, idx) => (
            <i key={idx} className={idx < hints ? "on" : "off"} />
          ))}
          <strong>{hints}</strong>
        </div>
        <div className="status-meta">
          <span>
            Score {teamScore}/{maxScore}
          </span>
          <span>Misfires {misfires}</span>
        </div>
      </div>

      <div className="player-list">
        {players.map((player) => (
          <div key={player.id} className="player-row">
            <span>{player.name}</span>
            <strong>0 ★</strong>
          </div>
        ))}
      </div>
    </aside>
  );
}
