import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import "./game.css";
import CardActionPopup from "./components/CardActionPopup";
import CardHintPopup from "./components/CardHintPopup";
import Deckcount from "./components/Deckcount";
import DiscardPanel from "./components/DiscardPanel";
import FireworksPanel from "./components/FireworksPanel";
import GameHeader from "./components/GameHeader";
import type { CardSelectPayload } from "./components/PlayerHand";
import PlayerHand from "./components/PlayerHand";
import TeamStatusPanel from "./components/TeamStatusPanel";
import type {
  CardColor,
  CardHintMarkers,
  CardValue,
  DiscardTableData,
  HandCard,
  Player,
} from "./types";

type GameState = {
  tableSize?: number;
};

type SelectedCardHint = {
  color: CardColor;
  value: CardValue;
  sameColorCount: number;
  sameValueCount: number;
  targetPlayerId: number;
  targetPlayerName: string;
  cardIndex: number;
  left: number;
  top: number;
};

type SelectedOwnCardAction = {
  color: CardColor;
  value: CardValue;
  cardIndex: number;
  left: number;
  top: number;
};

const HINT_POPUP_WIDTH = 200;
const HINT_POPUP_HEIGHT = 82;
const ACTION_POPUP_WIDTH = 200;
const ACTION_POPUP_HEIGHT = 82;
const POPUP_MARGIN = 8;
const POPUP_GAP = 10;
const HINT_API_ENDPOINT = "/api/hanabi/hint";
const PLAY_CARD_API_ENDPOINT = "/api/hanabi/play";
const DISCARD_CARD_API_ENDPOINT = "/api/hanabi/discard";
const CARD_COLORS: CardColor[] = ["Red", "White", "Yellow", "Green", "Blue"];

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function computePopupPosition(
  anchorRect: DOMRect,
  popupWidth: number,
  popupHeight: number,
  placement: "auto" | "right" | "left" = "auto",
): { left: number; top: number } {
  if (placement === "right") {
    const left = clamp(
      anchorRect.right + POPUP_GAP,
      POPUP_MARGIN,
      window.innerWidth - popupWidth - POPUP_MARGIN,
    );
    const centeredTop = anchorRect.top + (anchorRect.height - popupHeight) / 2;
    const top = clamp(centeredTop, POPUP_MARGIN, window.innerHeight - popupHeight - POPUP_MARGIN);

    return { left, top };
  }

  if (placement === "left") {
    const left = clamp(
      anchorRect.left - popupWidth - POPUP_GAP,
      POPUP_MARGIN,
      window.innerWidth - popupWidth - POPUP_MARGIN,
    );
    const centeredTop = anchorRect.top + (anchorRect.height - popupHeight) / 2;
    const top = clamp(centeredTop, POPUP_MARGIN, window.innerHeight - popupHeight - POPUP_MARGIN);

    return { left, top };
  }

  const preferredLeft = anchorRect.left + anchorRect.width / 2 - popupWidth / 2;
  const left = clamp(
    preferredLeft,
    POPUP_MARGIN,
    window.innerWidth - popupWidth - POPUP_MARGIN,
  );

  const topBelow = anchorRect.bottom + POPUP_GAP;
  const fitsBelow = topBelow + popupHeight <= window.innerHeight - POPUP_MARGIN;
  const topAbove = anchorRect.top - popupHeight - POPUP_GAP;

  return {
    left,
    top: fitsBelow ? topBelow : Math.max(POPUP_MARGIN, topAbove),
  };
}

function getDemoCard(playerId: number, cardIndex: number): HandCard {
  const color = CARD_COLORS[(playerId + cardIndex) % CARD_COLORS.length];
  const value = (((playerId + cardIndex) % 5) + 1) as CardValue;

  return { color, value };
}

function getDemoHand(playerId: number): HandCard[] {
  return Array.from({ length: 5 }, (_, cardIndex) => getDemoCard(playerId, cardIndex));
}

export default function Game() {
  const location = useLocation();
  const state = location.state as GameState | null;
  const tableSize = 4;
  const colors = ["Red", "Blue", "Green", "Yellow", "White"];
  const players: Player[] = Array.from({ length: tableSize }, (_, index) => ({
    id: index + 1,
    name: `Player ${index + 1}`,
  }));
  console.log(players)
  const fireworkValues = [2, 1, 3, 0, 0];
  const hints = 4;
  const misfires = 2;
  const deckCount = 34;
  const discardByColor: DiscardTableData = {
    Green: { 1: 2, 2: 1, 3: 0, 4: 0, 5: 0 },
    White: { 1: 1, 2: 2, 3: 1, 4: 0, 5: 0 },
    Red: { 1: 0, 2: 1, 3: 1, 4: 1, 5: 0 },
    Blue: { 1: 2, 2: 0, 3: 2, 4: 0, 5: 1 },
    Yellow: { 1: 1, 2: 1, 3: 0, 4: 1, 5: 0 },
  };
  const [selectedHint, setSelectedHint] = useState<SelectedCardHint | null>(null);
  const [selectedOwnCard, setSelectedOwnCard] = useState<SelectedOwnCardAction | null>(null);
  const [isSendingHint, setIsSendingHint] = useState(false);
  const [isSendingOwnCardAction, setIsSendingOwnCardAction] = useState(false);
  const [cardHintsByPlayer, setCardHintsByPlayer] = useState<
    Record<number, Record<number, CardHintMarkers>>
  >({});
  const currentPlayer = players[0];
  const handCardsByPlayer = new Map<number, HandCard[]>(
    players.map((player) => [player.id, getDemoHand(player.id)]),
  );
  console.log(handCardsByPlayer)
  let topPlayer: Player | undefined;
  let leftPlayer: Player | undefined;
  let rightPlayer: Player | undefined;

  if (tableSize <= 2) {
    topPlayer = players[1];
  } else if (tableSize === 3) {
    leftPlayer = players[1];
    topPlayer = players[2];
  } else {
    leftPlayer = players[1];
    topPlayer = players[2];
    rightPlayer = players[3];
  }

  const activePlayer = topPlayer?.name ?? currentPlayer.name;
  const currentPlayerCards = handCardsByPlayer.get(currentPlayer.id) ?? [];
  const topPlayerCards = topPlayer ? handCardsByPlayer.get(topPlayer.id) ?? [] : [];
  const leftPlayerCards = leftPlayer ? handCardsByPlayer.get(leftPlayer.id) ?? [] : [];
  const rightPlayerCards = rightPlayer ? handCardsByPlayer.get(rightPlayer.id) ?? [] : [];
  const tableClass = tableSize <= 2 ? "players-2" : tableSize === 3 ? "players-3" : "players-4";
  const applyHintToMatchingCards = (
    targetPlayerId: number,
    hintType: "color" | "number",
    hintValue: CardColor | CardValue,
  ) => {
    const targetCards = handCardsByPlayer.get(targetPlayerId) ?? [];

    setCardHintsByPlayer((current) => {
      const existingHintsForPlayer = current[targetPlayerId] ?? {};
      const nextHintsForPlayer: Record<number, CardHintMarkers> = {
        ...existingHintsForPlayer,
      };

      targetCards.forEach((card, cardIndex) => {
        const isMatchingCard =
          hintType === "color" ? card.color === hintValue : card.value === hintValue;

        if (!isMatchingCard) {
          return;
        }

        const existingCardHints = nextHintsForPlayer[cardIndex] ?? {};
        nextHintsForPlayer[cardIndex] =
          hintType === "color"
            ? { ...existingCardHints, colorHint: hintValue as CardColor }
            : { ...existingCardHints, numberHint: hintValue as CardValue };
      });

      return {
        ...current,
        [targetPlayerId]: nextHintsForPlayer,
      };
    });
  };

  const handleOtherCardSelect = ({
    color,
    value,
    sameColorCount,
    sameValueCount,
    popupPlacement,
    player,
    cardIndex,
    anchorRect,
  }: CardSelectPayload) => {
    const { left, top } = computePopupPosition(
      anchorRect,
      HINT_POPUP_WIDTH,
      HINT_POPUP_HEIGHT,
      popupPlacement,
    );

    setSelectedHint({
      color,
      value,
      sameColorCount,
      sameValueCount,
      targetPlayerId: player.id,
      targetPlayerName: player.name,
      cardIndex,
      left,
      top,
    });
    setSelectedOwnCard(null);
  };

  const handleCurrentCardSelect = ({ color, value, cardIndex, anchorRect }: CardSelectPayload) => {
    const preferredLeft = anchorRect.left + anchorRect.width / 2 - ACTION_POPUP_WIDTH / 2;
    const left = clamp(
      preferredLeft,
      POPUP_MARGIN,
      window.innerWidth - ACTION_POPUP_WIDTH - POPUP_MARGIN,
    );
    const preferredTop =
      anchorRect.top - ACTION_POPUP_HEIGHT - POPUP_GAP;
    const top =
      preferredTop >= POPUP_MARGIN
        ? preferredTop
        : clamp(
            anchorRect.bottom + POPUP_GAP,
            POPUP_MARGIN,
            window.innerHeight - ACTION_POPUP_HEIGHT - POPUP_MARGIN,
          );

    setSelectedOwnCard({
      color,
      value,
      cardIndex,
      left,
      top,
    });
    setSelectedHint(null);
  };

  const submitHint = async (hintType: "color" | "number") => {
    if (!selectedHint || isSendingHint) {
      return;
    }

    const hintValue = hintType === "color" ? selectedHint.color : selectedHint.value;

    try {
      setIsSendingHint(true);
      applyHintToMatchingCards(selectedHint.targetPlayerId, hintType, hintValue);
      await fetch(HINT_API_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          hintType,
          hintValue,
          fromPlayerId: currentPlayer.id,
          targetPlayerId: selectedHint.targetPlayerId,
          targetPlayerName: selectedHint.targetPlayerName,
          selectedCard: {
            index: selectedHint.cardIndex,
            color: selectedHint.color,
            value: selectedHint.value,
          },
        }),
      });
    } catch (error) {
      console.error("Failed to send hint selection to backend:", error);
    } finally {
      setIsSendingHint(false);
      setSelectedHint(null);
    }
  };

  const submitOwnCardAction = async (actionType: "play" | "discard") => {
    if (!selectedOwnCard || isSendingOwnCardAction) {
      return;
    }

    const endpoint =
      actionType === "play" ? PLAY_CARD_API_ENDPOINT : DISCARD_CARD_API_ENDPOINT;

    try {
      setIsSendingOwnCardAction(true);
      await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          actionType,
          playerId: currentPlayer.id,
          color: selectedOwnCard.color,
          value: selectedOwnCard.value,
          cardIndex: selectedOwnCard.cardIndex,
        }),
      });
    } catch (error) {
      console.error("Failed to send own card action to backend:", error);
    } finally {
      setIsSendingOwnCardAction(false);
      setSelectedOwnCard(null);
    }
  };

  useEffect(() => {
    if (!selectedHint && !selectedOwnCard) {
      return;
    }

    const closePopup = () => {
      if (isSendingHint || isSendingOwnCardAction) {
        return;
      }

      setSelectedHint(null);
      setSelectedOwnCard(null);
    };
    const handleOutsidePress = (event: MouseEvent) => {
      const target = event.target as HTMLElement | null;
      if (!target) {
        return;
      }

      if (
        target.closest(".card-hint-popup") ||
        target.closest(".card-action-popup") ||
        target.closest("[data-hint-card='true']")
      ) {
        return;
      }

      closePopup();
    };

    document.addEventListener("mousedown", handleOutsidePress);
    window.addEventListener("resize", closePopup);
    window.addEventListener("scroll", closePopup, true);

    return () => {
      document.removeEventListener("mousedown", handleOutsidePress);
      window.removeEventListener("resize", closePopup);
      window.removeEventListener("scroll", closePopup, true);
    };
  }, [isSendingHint, isSendingOwnCardAction, selectedHint, selectedOwnCard]);

  return (
    <section className="game-page">
      <GameHeader activePlayer={activePlayer} />

      <div className={`game-table ${tableClass}`.trim()}>
        {leftPlayer && (
          <PlayerHand
            player={leftPlayer}
            handCards={leftPlayerCards}
            cardHintsByCard={cardHintsByPlayer[leftPlayer.id]}
            hintPosition="right"
            orientation="vertical"
            cardRotationDeg={-90}
            nameSide="left"
            nameRotationDeg={90}
            hoverShift="right"
            popupPlacement="right-of-card"
            onCardSelect={handleOtherCardSelect}
            className="seat-left"
          />
        )}
        {topPlayer && (
          <PlayerHand
            player={topPlayer}
            handCards={topPlayerCards}
            cardHintsByCard={cardHintsByPlayer[topPlayer.id]}
            hintPosition="bottom"
            orientation="horizontal"
            hoverShift="down"
            onCardSelect={handleOtherCardSelect}
            className="seat-top"
          />
        )}
        {rightPlayer && (
          <PlayerHand
            player={rightPlayer}
            handCards={rightPlayerCards}
            cardHintsByCard={cardHintsByPlayer[rightPlayer.id]}
            hintPosition="left"
            orientation="vertical"
            cardRotationDeg={90}
            nameSide="right"
            nameRotationDeg={-90}
            hoverShift="left"
            popupPlacement="left-of-card"
            onCardSelect={handleOtherCardSelect}
            className="seat-right"
          />
        )}

        <main className="center-zone">
          <Deckcount deckCount={deckCount} />
          <FireworksPanel colors={colors} values={fireworkValues} misfires={misfires} />
        </main>

        <PlayerHand
          player={currentPlayer}
          handCards={currentPlayerCards}
          cardHintsByCard={cardHintsByPlayer[currentPlayer.id]}
          hintPosition="top"
          nameSide="bottom"
          isCurrentPlayer
          orientation="horizontal"
          hoverShift="up"
          onCardSelect={handleCurrentCardSelect}
          className="seat-bottom"
        />
        <DiscardPanel className="discard-bottom-left" discardByColor={discardByColor} />

        <TeamStatusPanel hints={hints} />
      </div>

      {selectedHint && (
        <CardHintPopup
          color={selectedHint.color}
          value={selectedHint.value}
          sameColorCount={selectedHint.sameColorCount}
          sameValueCount={selectedHint.sameValueCount}
          left={selectedHint.left}
          top={selectedHint.top}
          isSending={isSendingHint}
          onSelectColor={() => {
            void submitHint("color");
          }}
          onSelectNumber={() => {
            void submitHint("number");
          }}
        />
      )}
      {selectedOwnCard && (
        <CardActionPopup
          color={selectedOwnCard.color}
          value={selectedOwnCard.value}
          left={selectedOwnCard.left}
          top={selectedOwnCard.top}
          isSending={isSendingOwnCardAction}
          onPlay={() => {
            void submitOwnCardAction("play");
          }}
          onDiscard={() => {
            void submitOwnCardAction("discard");
          }}
        />
      )}
    </section>
  );
}
