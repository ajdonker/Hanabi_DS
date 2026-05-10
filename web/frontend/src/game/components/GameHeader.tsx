type GameHeaderProps = {
  activePlayer: string;
  gameOverScore: number | null;
};

export default function GameHeader({ activePlayer, gameOverScore }: GameHeaderProps) {
  if (gameOverScore !== null) {
    return (
      <header className="game-header">
        <div className="tutorial-icon"></div>
        <div className="tutorial-text">
          Game over. Final score: <strong>{gameOverScore}</strong>
        </div>
      </header>
    );
  }

  return (
    <header className="game-header">
      <div className="tutorial-icon"></div>
      <div className="tutorial-text">
        <strong>{activePlayer}</strong> must play a card, discard a card, or give
        a clue to a teammate.
      </div>
    </header>
  );
}
