type DeckcountProps = {
  deckCount: number;
};

export default function Deckcount({ deckCount }: DeckcountProps) {
  return (
    <div className="deckcount">
      <div className="deck-stack">
        <div className="deck-card-skin" />
        <div className="deck-count-out">{deckCount}</div>
      </div>
    </div>
  );
}
