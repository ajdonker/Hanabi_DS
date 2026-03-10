export type Player = {
  id: number;
  name: string;
};

export type CardColor = "Green" | "White" | "Red" | "Blue" | "Yellow";
export type CardValue = 1 | 2 | 3 | 4 | 5;

export type DiscardCounts = {
  ones: number;
  twos: number;
  threes: number;
};

export type DiscardTableData = Record<CardColor, DiscardCounts>;
