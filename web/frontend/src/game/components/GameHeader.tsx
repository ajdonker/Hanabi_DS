type GameHeaderProps = {
  tableId: string;
  tableSize: number;
};

export default function GameHeader({ tableId, tableSize }: GameHeaderProps) {
  return (
    <header className="game-header">
      <div className="tutorial-icon">🎓</div>
      <div className="tutorial-text">
        <strong>Table {tableId}</strong> | {tableSize} players must play a card,
        discard a card, or give a clue.
      </div>
    </header>
  );
}
