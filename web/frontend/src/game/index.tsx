import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
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
import { toRectShape, animateOwnCardAction, drawCardToPlayerHand } from "./animate";
import { colors } from "./config";
import { useGameState } from "./useGameState";
import type {
  CardColor,
  CardValue,
  HandCard,
  Player,
  FlyingCard,
  SelectedOwnCardAction,
  Direction
} from "./types";

type SelectedCardHint = {
  color: CardColor;
  value: CardValue;
  sameColorCount: number;
  sameValueCount: number;
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

export default function Game() {
  const { tableId: routeGameId } = useParams();
  const {
    activePlayerName,
    cardHintsByPlayer,
    deckCount,
    discardByColor,
    fireworkValues,
    gameActionError,
    gameSocketStatus,
    gameSocketUrl,
    giveHint,
    handCardsByPlayer,
    hints,
    lastGameEventMessage,
    misfires,
    playCard,
    players,
    discardCard,
    setHandCardsByPlayer,
  } = useGameState(routeGameId);
  const currentPlayer = players[0];
  const [selectedHint, setSelectedHint] = useState<SelectedCardHint | null>(null);
  const [selectedOwnCard, setSelectedOwnCard] = useState<SelectedOwnCardAction | null>(null);
  const [flyingCard, setFlyingCard] = useState<FlyingCard | null>(null);
  const [isSendingHint, setIsSendingHint] = useState(false);
  const [isSendingOwnCardAction, setIsSendingOwnCardAction] = useState(false);
  let topPlayer: Player | undefined;
  let leftPlayer: Player | undefined;
  let rightPlayer: Player | undefined;

  const effectiveTableSize = players.length;
  if (effectiveTableSize <= 2) {
    topPlayer = players[1];
  } else if (effectiveTableSize === 3) {
    leftPlayer = players[1];
    topPlayer = players[2];
  } else {
    leftPlayer = players[1];
    topPlayer = players[2];
    rightPlayer = players[3];
  }

  const activePlayer = activePlayerName || topPlayer?.name || currentPlayer.name;
  const currentPlayerCards = handCardsByPlayer[currentPlayer.id] ?? [];
  const topPlayerCards = topPlayer ? handCardsByPlayer[topPlayer.id] ?? [] : [];
  const leftPlayerCards = leftPlayer ? handCardsByPlayer[leftPlayer.id] ?? [] : [];
  const rightPlayerCards = rightPlayer ? handCardsByPlayer[rightPlayer.id] ?? [] : [];
  const tableClass = effectiveTableSize <= 2 ? "players-2" : effectiveTableSize === 3 ? "players-3" : "players-4";

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
      await giveHint(
        currentPlayer.name,
        selectedHint.targetPlayerName,
        hintType,
        hintValue,
      );
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
    const command = actionType === "play" ? playCard : discardCard;

    try {
      setIsSendingOwnCardAction(true);
      setSelectedOwnCard(null);
      const result = await command(currentPlayer.name, ownCardAction.cardIndex);
      const playAnimationPromise = animateOwnCardAction(actionType, ownCardAction, setFlyingCard);
      await playAnimationPromise;
      const playedWrongCard = result.events.some((event) => event.event === "card_wrong");
      if (actionType === "play" && playedWrongCard) {
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

  const handleTestDrawCard = async (playerId: number) => {
    let playerDirection: Direction;
    if (playerId == topPlayer?.id) {
      playerDirection = 'top';
    } else if (playerId === leftPlayer?.id) {
      playerDirection = 'left';
    } else if (playerId === rightPlayer?.id) {
      playerDirection = 'right';
    } else {
      playerDirection = 'bottom';
    }

    const newCard: HandCard = {
      color: colors[Math.floor(Math.random() * colors.length)],
      value: (Math.floor(Math.random() * 5) + 1) as CardValue,
    };

    await drawCardToPlayerHand(newCard, playerDirection, setFlyingCard);

    setHandCardsByPlayer((current) => {
      const ownCards = current[playerId] ?? [];
      let newCards: HandCard[];
      if (playerDirection === 'bottom' || playerDirection === 'left') {
        newCards = [newCard, ...ownCards];
        
      } else {
        newCards = [...ownCards, newCard];
      }
      return {
        ...current,
        [playerId]: newCards,
      };
    });
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
      <div className={`game-socket-status is-${gameSocketStatus}`}>
        Game server: {gameSocketStatus}
        {gameSocketUrl ? ` (${gameSocketUrl})` : ""}
      </div>
      {(gameActionError || lastGameEventMessage) && (
        <div className={`game-event-message ${gameActionError ? "is-error" : ""}`.trim()}>
          {gameActionError || lastGameEventMessage}
        </div>
      )}

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
          <button onClick={() => handleTestDrawCard(4)}>Draw Card</button>
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
