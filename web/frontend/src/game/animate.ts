const OWN_CARD_FLY_DURATION_MS = 420;
const OWN_CARD_FADE_DURATION_MS = 180;

import type {
  CardColor,
  FlyingCard,
  SelectedOwnCardAction
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