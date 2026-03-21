import type { CardColor, CardValue } from "../types";

type CardActionPopupProps = {
  color: CardColor;
  value: CardValue;
  left: number;
  top: number;
  isSending?: boolean;
  onPlay: () => void;
  onDiscard: () => void;
};
// todo _colr and _value are not used, consider removing them
export default function CardActionPopup({
  color: _color,
  value: _value,
  left,
  top,
  isSending = false,
  onPlay,
  onDiscard,
}: CardActionPopupProps) {
  return (
    <aside
      className="card-action-popup"
      style={{ left, top }}
    >
      <button
        type="button"
        className="card-action-button"
        onClick={onPlay}
        disabled={isSending}
      >
        Play selected card
      </button>
      <button
        type="button"
        className="card-action-button"
        onClick={onDiscard}
        disabled={isSending}
      >
        Discard selected card
      </button>
    </aside>
  );
}
