import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import "./game.css";
import CardActionPopup from "./components/CardActionPopup";
import CardHintPopup from "./components/CardHintPopup";
import FlyingCardComponent from "./components/FlyingCard";
import Deckcount from "./components/Deckcount";
import DiscardPanel from "./components/DiscardPanel";
import FireworksPanel from "./components/FireworksPanel";
import GameHeader from "./components/GameHeader";
import type { CardSelectPayload } from "./components/PlayerHand";
import PlayerHand from "./components/PlayerHand";
import TeamStatusPanel from "./components/TeamStatusPanel";
import { toRectShape, animateOwnCardAction} from "./animate";
import type {
  CardColor,
  CardHintMarkers,
  CardValue,
  DiscardTableData,
  HandCard,
  Player,
  FlyingCard,
  SelectedOwnCardAction
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


const HINT_POPUP_WIDTH = 200;
const HINT_POPUP_HEIGHT = 82;
const ACTION_POPUP_WIDTH = 200;
const ACTION_POPUP_HEIGHT = 82;
const POPUP_GAP = 10;
const HINT_API_ENDPOINT = "/api/hanabi/hint";
const PLAY_CARD_API_ENDPOINT = "/api/hanabi/play";
const DISCARD_CARD_API_ENDPOINT = "/api/hanabi/discard";
const CARD_COLORS: CardColor[] = ["Red", "White", "Yellow", "Green", "Blue"];

function computePopupPosition(
  anchorRect: DOMRect,
  popupWidth: number,
  popupHeight: number,
  placement: "below" | "right" | "left" = "below",
): { left: number; top: number } {
  if (placement === "right") {
    const left = anchorRect.right + POPUP_GAP;
    const top = anchorRect.top + (anchorRect.height - popupHeight) / 2;

    return { left, top };
  }

  if (placement === "left") {
    const left = anchorRect.left - popupWidth - POPUP_GAP;
    const top = anchorRect.top + (anchorRect.height - popupHeight) / 2;

    return { left, top };
  }
  // for "below" placement
  const left = anchorRect.left + (anchorRect.width - popupWidth) / 2;
  const top = anchorRect.bottom + POPUP_GAP;

  return { left, top };
}

function getDemoCard(playerId: number, cardIndex: number): HandCard {
  const color = CARD_COLORS[(playerId + cardIndex) % CARD_COLORS.length];
  const value = (((playerId + cardIndex) % 5) + 1) as CardValue;

  return { color, value };
}

function getDemoHand(playerId: number): HandCard[] {
  return Array.from({ length: 5 }, (_, cardIndex) => getDemoCard(playerId, cardIndex));
}

function createDemoHandsByPlayer(players: Player[]): Record<number, HandCard[]> {
  return players.reduce<Record<number, HandCard[]>>((hands, player) => {
    hands[player.id] = getDemoHand(player.id);
    return hands;
  }, {});
}

export default function Game() {
  const location = useLocation();
  const state = location.state as GameState | null;
  const tableSize = Math.max(2, Math.min(4, state?.tableSize ?? 4));

  const players: Player[] = Array.from({ length: tableSize }, (_, index) => ({
    id: index + 1,
    name: `Player ${index + 1}`,
  }));
  const currentPlayer = players[0];
  const fireworkValues: CardValue[] = [2, 1, 0, 4, 5];
  const hints = 4;
  const misfires = 2;
  const deckCount = 34;
  const discardByColor: DiscardTableData = {
    Red : { 0: 0, 1: 2, 2: 1, 3: 0, 4: 0, 5: 0 },
    Blue : { 0: 0, 1: 1, 2: 2, 3: 1, 4: 0, 5: 0 },
    Green: { 0: 0, 1: 0, 2: 1, 3: 1, 4: 1, 5: 0 },
    Yellow: { 0: 0, 1: 1, 2: 1, 3: 0, 4: 1, 5: 0 },
    White: { 0: 0, 1: 2, 2: 0, 3: 2, 4: 0, 5: 1 },
  };
  const [selectedHint, setSelectedHint] = useState<SelectedCardHint | null>(null);
  const [selectedOwnCard, setSelectedOwnCard] = useState<SelectedOwnCardAction | null>(null);
  const [flyingCard, setFlyingCard] = useState<FlyingCard | null>(null);
  const [handCardsByPlayer, setHandCardsByPlayer] = useState<Record<number, HandCard[]>>(() =>
    createDemoHandsByPlayer(players),
  );
  const [isSendingHint, setIsSendingHint] = useState(false);
  const [isSendingOwnCardAction, setIsSendingOwnCardAction] = useState(false);
  const [cardHintsByPlayer, setCardHintsByPlayer] = useState<
    Record<number, Record<number, CardHintMarkers>>
  >({});
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

  const activePlayer = topPlayer?.name ?? currentPlayer.name; // todo in real game state, active player can be any of the players, not just top player. Adjust accordingly when integrating with real backend data
  const currentPlayerCards = handCardsByPlayer[currentPlayer.id] ?? [];
  const topPlayerCards = topPlayer ? handCardsByPlayer[topPlayer.id] ?? [] : [];
  const leftPlayerCards = leftPlayer ? handCardsByPlayer[leftPlayer.id] ?? [] : [];
  const rightPlayerCards = rightPlayer ? handCardsByPlayer[rightPlayer.id] ?? [] : [];
  const tableClass = tableSize <= 2 ? "players-2" : tableSize === 3 ? "players-3" : "players-4";
  const applyHintToMatchingCards = (
    targetPlayerId: number,
    hintType: "color" | "number",
    hintValue: CardColor | CardValue,
  ) => {
    const targetCards = handCardsByPlayer[targetPlayerId] ?? [];

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
    const left = anchorRect.left + anchorRect.width / 2 - ACTION_POPUP_WIDTH / 2;
    const top = anchorRect.top - ACTION_POPUP_HEIGHT - POPUP_GAP;

    setSelectedOwnCard({
      color,
      value,
      cardIndex,
      left,
      top,
      anchorRect: toRectShape(anchorRect),
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

    const ownCardAction = selectedOwnCard;
    const endpoint =
      actionType === "play" ? PLAY_CARD_API_ENDPOINT : DISCARD_CARD_API_ENDPOINT;

    try {
      setIsSendingOwnCardAction(true);
      setHandCardsByPlayer((current) => {
        const ownCards = current[currentPlayer.id] ?? [];
        return {
          ...current,
          [currentPlayer.id]: ownCards.filter((_, index) => index !== ownCardAction.cardIndex),
        };
      });
      setSelectedOwnCard(null);
      const playAnimationPromise = animateOwnCardAction(actionType, ownCardAction, setFlyingCard);
      await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          actionType,
          playerId: currentPlayer.id,
          color: ownCardAction.color,
          value: ownCardAction.value,
          cardIndex: ownCardAction.cardIndex,
        }),
      });
      await playAnimationPromise;
      // todo if drop wrong card, revise
      console.log("in try block, after play animation");
      if (actionType == "play") {
        // todo show some error message to user
        const discardAnimationPromise = animateOwnCardAction('discard', ownCardAction, setFlyingCard);
        await discardAnimationPromise;
      }
    } catch (error) {
      console.log("in catch block, before animation");
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
        target.closest(".card-action-popup")
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
            nameRotationDeg={180}
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
            nameRotationDeg={0}
            hoverShift="left"
            popupPlacement="left-of-card"
            onCardSelect={handleOtherCardSelect}
            className="seat-right"
          />
        )}

        <main className="center-zone">
          <Deckcount deckCount={deckCount} />
          <FireworksPanel values={fireworkValues} misfires={misfires} />
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
      {flyingCard && <FlyingCardComponent {...flyingCard} />}
    </section>
  );
}
