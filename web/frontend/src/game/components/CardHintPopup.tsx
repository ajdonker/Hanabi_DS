import type { CardColor, CardValue } from "../types";

type CardHintPopupProps = {
  color: CardColor;
  value: CardValue;
  sameColorCount: number;
  sameValueCount: number;
  left: number;
  top: number;
  isSending?: boolean;
  onSelectColor: () => void;
  onSelectNumber: () => void;
  onPlay: () => void;
  onDiscard: () => void;
};

const VALUE_WORDS: Record<CardValue, { single: string; plural: string }> = {
  1: { single: "One", plural: "Ones" },
  2: { single: "Two", plural: "Twos" },
  3: { single: "Three", plural: "Threes" },
  4: { single: "Four", plural: "Fours" },
  5: { single: "Five", plural: "Fives" },
  0: {
    single: "",
    plural: ""
  }
};

export default function CardHintPopup({
  color,
  value,
  sameColorCount,
  sameValueCount,
  left,
  top,
  isSending = false,
  onSelectColor,
  onSelectNumber,
  onPlay,
  onDiscard
}: CardHintPopupProps) {
  const normalizedColor = color.toLowerCase();
  const pluralValueWord = VALUE_WORDS[value].plural;
  const singularValueWord = VALUE_WORDS[value].single.toUpperCase();

  return (
    <aside className="card-hint-popup" style={{ left, top }} role="dialog">
      <button
        type="button"
        className="card-hint-line card-hint-action"
        onClick={onSelectColor}
        disabled={isSending}
      >
        {sameColorCount > 1 ? (
          <>
            These {sameColorCount} cards are{" "}
            <span className={`card-hint-color ${normalizedColor}`.trim()}>{normalizedColor}</span>
          </>
        ) : (
          <>
            This card is <span className={`card-hint-color ${normalizedColor}`.trim()}>{color}</span>
          </>
        )}
      </button>
      <button
        type="button"
        className="card-hint-line card-hint-action"
        onClick={onSelectNumber}
        disabled={isSending}
      >
        {sameValueCount > 1 ? (
          <>
            These {sameValueCount} cards are <strong>{pluralValueWord}</strong>
          </>
        ) : (
          <>
            This card is a <strong>{singularValueWord}</strong>
          </>
        )}
      </button>
      <span onClick={onPlay}>play</span>
      <span onClick={onDiscard}>discard</span>
    </aside>
  );
}
