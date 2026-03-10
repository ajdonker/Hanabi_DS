type GameHeaderProps = {
  activePlayer: string;
};

export default function GameHeader({ activePlayer }: GameHeaderProps) {
  return (
    <header className="game-header">
      <div className="tutorial-icon">🎓</div>
      <div className="tutorial-text">
        <strong>{activePlayer}</strong> must play a card, discard a card, or give
        a clue to a teammate.
      </div>
    </header>
  );
}
