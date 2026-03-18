import {CARD_WIDTH, CARD_HEIGHT, CARD_GAP} from "./config";

const OWN_CARD_FLY_DURATION_MS = 420;
const OWN_CARD_FADE_DURATION_MS = 180;

import type {
  CardColor,
  HandCard,
  FlyingCard,
  SelectedOwnCardAction,
  Direction,
} from "./types";

function wait(durationMs: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, durationMs);
  });
}

export function toRectShape(rect: DOMRect) {
  return {
    left: rect.left,
    top: rect.top,
    width: rect.width,
    height: rect.height,
  };
}

function resolveOwnCardTargetRect(
  actionType: "play" | "discard",
  color: CardColor,
  sourceRect: { left: number; top: number; width: number; height: number },
) {
  if (actionType === "play") {
    const laneElement = document.querySelector<HTMLElement>(
      `.firework-lane.${color.toLowerCase()}`,
    );
    if (laneElement) {
      const laneRect = laneElement.getBoundingClientRect();
      return {
        left: laneRect.left + 6,
        top: laneRect.top + 28,
        width: sourceRect.width,
        height: sourceRect.height,
      };
    }
  } else {
    const discardPanel = document.querySelector<HTMLElement>(".discard-panel");
    if (discardPanel) {
      const panelRect = discardPanel.getBoundingClientRect();
      return {
        left: panelRect.left,
        top: panelRect.top,
        width: sourceRect.width,
        height: sourceRect.height,
      };
    }
  }

  return sourceRect;
}

function resolveDeckSourceRect() {
  const deckElement = document.querySelector<HTMLElement>(".deck-stack");
  if (deckElement) {
    const rect = deckElement.getBoundingClientRect();
    return {
      left: rect.left,
      top: rect.top,
      width: CARD_WIDTH,
      height: CARD_HEIGHT,
    };
  }

  throw new Error("Deck element not found");
}

function resolvePlayerDrawTargetRect(
  direction: Direction,
) {
  const targetHandElement = document.querySelector<HTMLElement>(`.player-hand.seat-${direction} .hand-cards`);
  if (!targetHandElement) {
    throw new Error(`Player hand element for direction ${direction} not found`);
  }

  let lastCardWrapper: HTMLElement | null = null;
  if (direction === "bottom" || direction === "left") {
    lastCardWrapper = targetHandElement.querySelector<HTMLElement>(".card-hover-wrap:first-child");
  } else {
   lastCardWrapper = targetHandElement.querySelector<HTMLElement>(".card-hover-wrap:last-child");
  }
  


  if (lastCardWrapper) {
    const lastRect = lastCardWrapper.getBoundingClientRect();
    let newLeft: number;
    let newTop: number;
    let newWidth = 0;
    let newHeight = 0;
    if (direction === "bottom") {
      newLeft = lastRect.left - CARD_WIDTH - CARD_GAP;
      newTop = lastRect.top;
      newWidth = CARD_WIDTH;
      newHeight = CARD_HEIGHT;
    } else if (direction === "top") {
      newLeft = lastRect.right + CARD_GAP;
      newTop = lastRect.top;
      newWidth = CARD_WIDTH;
      newHeight = CARD_HEIGHT;
    } else if (direction === "left") {
      newLeft = lastRect.left;
      newTop = lastRect.top - CARD_WIDTH - CARD_GAP;
      newWidth = CARD_HEIGHT;
      newHeight = CARD_WIDTH;
    } else {
      newLeft = lastRect.left;
      newTop = lastRect.top + CARD_GAP;
      newWidth = CARD_HEIGHT;
      newHeight = CARD_WIDTH;
    }
    return {
      left: newLeft,
      top: newTop,
      width: newWidth,
      height: newHeight,
    };
  }
  throw new Error(`No cards found in player hand for direction ${direction}`);
}

export const drawCardToPlayerHand = async (
    newCard: HandCard,
    direction: Direction,
    setFlyingCard: React.Dispatch<React.SetStateAction<FlyingCard | null>>,
  ) => {
    const fromRect = resolveDeckSourceRect();
    const toRect = resolvePlayerDrawTargetRect(direction);
    let rotationDeg = 0;
    if (direction === "left") {
      rotationDeg = 90;
    } else if (direction === "top") {
      rotationDeg = 180;
    } else if (direction === "right") {
      rotationDeg = -90;
    }
    setFlyingCard({
      color: newCard.color,
      value: newCard.value,
      fromRect,
      toRect,
      state: "idle",
      rotationDeg,
    });

    await new Promise<void>((resolve) => {
      window.requestAnimationFrame(() => resolve());
    });
    setFlyingCard((current) => (current ? { ...current, state: "moving" } : null));
    await wait(OWN_CARD_FLY_DURATION_MS * 1);
    setFlyingCard((current) => (current ? { ...current, state: "fading" } : null));
    await wait(OWN_CARD_FADE_DURATION_MS * 1);
    setFlyingCard(null);
  }
export const animateOwnCardAction = async (
    actionType: "play" | "discard",
    ownCard: SelectedOwnCardAction,
    setFlyingCard: React.Dispatch<React.SetStateAction<FlyingCard | null>>,
  ) => {
    const fromRect = ownCard.anchorRect;
    const toRect = resolveOwnCardTargetRect(actionType, ownCard.color, fromRect);

    setFlyingCard({
      color: ownCard.color,
      value: ownCard.value,
      fromRect,
      toRect,
      state: "idle",
    });

    await new Promise<void>((resolve) => {
      window.requestAnimationFrame(() => resolve());
    });
    setFlyingCard((current) => (current ? { ...current, state: "moving" } : null));
    await wait(OWN_CARD_FLY_DURATION_MS * 1);
    setFlyingCard((current) => (current ? { ...current, state: "fading" } : null));
    await wait(OWN_CARD_FADE_DURATION_MS * 1);
    setFlyingCard(null);
  };
