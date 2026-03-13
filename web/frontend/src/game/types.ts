export type Player = {
  id: number;
  name: string;
};

export type CardColor = "Green" | "White" | "Red" | "Blue" | "Yellow";
export type CardValue = 1 | 2 | 3 | 4 | 5;
export type HandCard = {
  color: CardColor;
  value: CardValue;
};

export type CardHintMarkers = {
  numberHint?: CardValue;
  colorHint?: CardColor;
};

export type DiscardCounts = Record<CardValue, number>;

export type DiscardTableData = Record<CardColor, DiscardCounts>;
