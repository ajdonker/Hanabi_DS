export type Player = {
  id: number;
  name: string;
};

export type CardColor = "Green" | "White" | "Red" | "Blue" | "Yellow";
export type CardValue = 0 | 1 | 2 | 3 | 4 | 5;
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

export type FlyingCard = {
  color: CardColor;
  value: CardValue;
  fromRect: {
    left: number;
    top: number;
    width: number;
    height: number;
  };
  toRect: {
    left: number;
    top: number;
    width: number;
    height: number;
  };
  state: "idle" | "moving" | "fading";
};

export type SelectedOwnCardAction = {
  color: CardColor;
  value: CardValue;
  cardIndex: number;
  left: number;
  top: number;
  anchorRect: {
    left: number;
    top: number;
    width: number;
    height: number;
  };
};
