import { useCallback, useEffect, useRef, useState } from "react";
import { getEventData, HanabiWsClient, type ServerEvent } from "../network/wsClient";
import { colors } from "./config";
import type {
  CardColor,
  CardHintMarkers,
  CardValue,
  DiscardTableData,
  FireworkValue,
  HandCard,
  Player,
} from "./types";

export type GameSocketStatus = "missing" | "connecting" | "connected" | "closed" | "error";

export type GameCommandResult = {
  cardAction: CardActionAnimationEvent | null;
  drawnCard: DrawnCardEvent | null;
  events: ServerEvent[];
  gameOverScore: number | null;
};

type HandledGameEvents = GameCommandResult & {
  errorMessage: string;
  hasError: boolean;
  hasGameState: boolean;
};

export type DrawnCardEvent = {
  card: HandCard;
  cardIndex: number;
  playerName: string;
  sequence: number;
};

export type CardActionAnimationEvent = {
  actionType: "play" | "discard";
  drawnCard: DrawnCardEvent | null;
  playerName: string;
  removedCardIndex: number;
  sequence: number;
};

type BackendHandCard = {
  number: CardValue;
  color: CardColor;
  hints: {
    color: CardColor | null;
    number: CardValue | null;
  };
};

type BackendPlayer = {
  username: string;
  hand: BackendHandCard[];
  last_turn: boolean;
};

type BackendGameState = {
  game_id: string;
  player_turn: string;
  final_turn: boolean;
  players: BackendPlayer[];
  board: {
    piles: Partial<Record<CardColor, number>>;
    discards: Array<{
      number: CardValue;
      color: CardColor;
    }>;
    tokens: number;
    misfires: number;
    deck_count: number;
  };
};

type BackendDrawnCardEvent = {
  playerId?: unknown;
  cardIndex?: unknown;
  card?: {
    number?: unknown;
    color?: unknown;
  };
};

const COLOR_BY_BACKEND: Record<string, CardColor> = {
  RED: "Red",
  YELLOW: "Yellow",
  GREEN: "Green",
  BLUE: "Blue",
  WHITE: "White",
};

const VALUE_BY_BACKEND: Record<string, CardValue> = {
  ONE: 1,
  TWO: 2,
  THREE: 3,
  FOUR: 4,
  FIVE: 5,
};

const COLOR_TO_BACKEND: Record<CardColor, string> = {
  Red: "RED",
  Yellow: "YELLOW",
  Green: "GREEN",
  Blue: "BLUE",
  White: "WHITE",
};

const VALUE_TO_BACKEND: Record<CardValue, string> = {
  1: "ONE",
  2: "TWO",
  3: "THREE",
  4: "FOUR",
  5: "FIVE",
};

function createPlaceholderHandsByPlayer(players: Player[]): Record<number, HandCard[]> {
  return players.reduce<Record<number, HandCard[]>>((hands, player) => {
    hands[player.id] = [{ color: "Blue", value: 1 }];
    return hands;
  }, {});
}

function createEmptyDiscardByColor(): DiscardTableData {
  return colors.reduce<DiscardTableData>((discardByColor, color) => {
    discardByColor[color] = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
    return discardByColor;
  }, {} as DiscardTableData);
}

function normalizeColor(color: string): CardColor {
  return COLOR_BY_BACKEND[color] ?? (color as CardColor);
}

function normalizeValue(value: string | number): CardValue {
  return VALUE_BY_BACKEND[String(value)] ?? (value as CardValue);
}

function normalizeGameState(gameState: BackendGameState): BackendGameState {
  return {
    ...gameState,
    players: gameState.players.map((player) => ({
      ...player,
      hand: player.hand.map((card) => ({
        ...card,
        number: normalizeValue(card.number),
        color: normalizeColor(card.color),
        hints: {
          ...card.hints,
          color: card.hints.color ? normalizeColor(card.hints.color) : null,
          number: card.hints.number ? normalizeValue(card.hints.number) : null,
        },
      })),
    })),
    board: {
      ...gameState.board,
      piles: Object.fromEntries(
        Object.entries(gameState.board.piles).map(([color, value]) => [
          normalizeColor(color),
          value,
        ]),
      ) as Partial<Record<CardColor, number>>,
      discards: gameState.board.discards.map((card) => ({
        ...card,
        number: normalizeValue(card.number),
        color: normalizeColor(card.color),
      })),
    },
  };
}

function getCurrentPlayerName(): string | null {
  return localStorage.getItem("hanabi.username") ||
    localStorage.getItem("hanabi.playerId");
}

function toFrontendCard(card: BackendHandCard): HandCard {
  return {
    color: card.color,
    value: card.number,
  };
}

function toDrawnCardEvent(
  data: Record<string, unknown>,
  sequence: number,
): DrawnCardEvent | null {
  const event = data as BackendDrawnCardEvent;
  if (
    typeof event.playerId !== "string" ||
    typeof event.cardIndex !== "number" ||
    !event.card ||
    typeof event.card.color !== "string" ||
    typeof event.card.number !== "string"
  ) {
    return null;
  }

  return {
    playerName: event.playerId,
    cardIndex: event.cardIndex,
    card: {
      color: normalizeColor(event.card.color),
      value: normalizeValue(event.card.number),
    },
    sequence,
  };
}

function rotatePlayersForCurrentUser(
  players: BackendPlayer[],
  currentPlayerName: string | null,
): BackendPlayer[] {
  if (!currentPlayerName) {
    return players;
  }

  const currentPlayerIndex = players.findIndex(
    (player) => player.username === currentPlayerName,
  );

  if (currentPlayerIndex <= 0) {
    return players;
  }

  return [
    ...players.slice(currentPlayerIndex),
    ...players.slice(0, currentPlayerIndex),
  ];
}

export function useGameState(routeGameId: string | undefined) {
  const clientRef = useRef<HanabiWsClient | null>(null);
  const cardActionSequenceRef = useRef(0);
  const placeholderPlayers: Player[] = [{
    id: 1,
    name: "Placeholder Player",
  }];
  const [players, setPlayers] = useState<Player[]>(placeholderPlayers);
  const [handCardsByPlayer, setHandCardsByPlayer] = useState<Record<number, HandCard[]>>(() =>
    createPlaceholderHandsByPlayer(placeholderPlayers),
  );
  const [cardHintsByPlayer, setCardHintsByPlayer] = useState<
    Record<number, Record<number, CardHintMarkers>>
  >({});
  const [fireworkValues, setFireworkValues] = useState<FireworkValue[]>([0, 0, 0, 0, 0]);
  const [hints, setHints] = useState(8);
  const [misfires, setMisfires] = useState(0);
  const [deckCount, setDeckCount] = useState(0);
  const [discardByColor, setDiscardByColor] = useState<DiscardTableData>(() =>
    createEmptyDiscardByColor(),
  );
  const [activePlayerName, setActivePlayerName] = useState("");
  const [gameSocketStatus, setGameSocketStatus] =
    useState<GameSocketStatus>("connecting");
  const [gameSocketUrl, setGameSocketUrl] = useState("");
  const [gameActionError, setGameActionError] = useState("");
  const [lastGameEventMessage, setLastGameEventMessage] = useState("");
  const [lastCardAction, setLastCardAction] = useState<CardActionAnimationEvent | null>(null);

  const applyGameState = useCallback((gameState: BackendGameState) => {
    console.log("Received game state:", gameState);
    const orderedBackendPlayers = rotatePlayersForCurrentUser(
      gameState.players,
      getCurrentPlayerName(),
    );
    const orderedPlayers = orderedBackendPlayers.map<Player>((player, index) => ({
      id: index + 1,
      name: player.username,
    }));
    const nextHandsByPlayer: Record<number, HandCard[]> = {};
    const nextHintsByPlayer: Record<number, Record<number, CardHintMarkers>> = {};

    orderedBackendPlayers.forEach((backendPlayer, playerIndex) => {
      const playerId = playerIndex + 1;
      nextHandsByPlayer[playerId] = backendPlayer.hand.map(toFrontendCard);

      backendPlayer.hand.forEach((card, cardIndex) => {
        const hintsForCard: CardHintMarkers = {};
        if (card.hints.color) {
          hintsForCard.colorHint = card.hints.color;
        }
        if (card.hints.number) {
          hintsForCard.numberHint = card.hints.number;
        }
        if (hintsForCard.colorHint || hintsForCard.numberHint) {
          nextHintsByPlayer[playerId] = {
            ...nextHintsByPlayer[playerId],
            [cardIndex]: hintsForCard,
          };
        }
      });
    });

    const nextDiscardByColor = createEmptyDiscardByColor();
    gameState.board.discards.forEach((card) => {
      const color = card.color;
      const value = card.number;
      nextDiscardByColor[color][value] += 1;
    });

    setPlayers(orderedPlayers);
    setHandCardsByPlayer(nextHandsByPlayer);
    setCardHintsByPlayer(nextHintsByPlayer);
    setFireworkValues(
      colors.map((color) => {
        const pileValue = gameState.board.piles[color] ?? 0;
        return Math.max(0, Math.min(5, pileValue)) as FireworkValue;
      }),
    );
    setDiscardByColor(nextDiscardByColor);
    setHints(gameState.board.tokens);
    setMisfires(gameState.board.misfires);
    setDeckCount(gameState.board.deck_count);
    setActivePlayerName(gameState.player_turn);
  }, []);

  const applyGameStateFromEvents = useCallback((events: ServerEvent[]) => {
    const gameState = getEventData<BackendGameState>(events, "game_state");
    if (!gameState) {
      return false;
    }

    applyGameState(normalizeGameState(gameState));
    return true;
  }, [applyGameState]);

  const handleReturnedGameEvents = useCallback((
    events: ServerEvent[],
    options: { publishCardAction?: boolean } = {},
  ): HandledGameEvents => {
    let actionType: "play" | "discard" | null = null;
    let actionPlayerName = "";
    let removedCardIndex: number | null = null;
    let cardAction: CardActionAnimationEvent | null = null;
    let drawnCard: DrawnCardEvent | null = null;
    let drawnCardSequence: number | null = null;
    let errorMessage = "";
    let hasError = false;
    let gameOverScore: number | null = null;
    const hasGameState = applyGameStateFromEvents(events);

    events.forEach(({ event, data }) => {
      if (event === "error") {
        hasError = true;
        errorMessage = typeof data.message === "string" ? data.message : "Game command failed.";
        setGameActionError(errorMessage);
        return;
      }

      if (event === "card_correct") {
        if (typeof data.playerId === "string" && typeof data.cardIndex === "number") {
          actionType = "play";
          actionPlayerName = data.playerId;
          removedCardIndex = data.cardIndex;
        }
        setLastGameEventMessage("Card played.");
        return;
      }

      if (event === "card_wrong") {
        if (typeof data.playerId === "string" && typeof data.cardIndex === "number") {
          actionType = "play";
          actionPlayerName = data.playerId;
          removedCardIndex = data.cardIndex;
        }
        setLastGameEventMessage("Card misfired.");
        return;
      }

      if (event === "card_discarded") {
        if (typeof data.playerId === "string" && typeof data.cardIndex === "number") {
          actionType = "discard";
          actionPlayerName = data.playerId;
          removedCardIndex = data.cardIndex;
        }
        setLastGameEventMessage("Card discarded.");
        return;
      }

      if (event === "card_drawn") {
        const nextDrawnCard = toDrawnCardEvent(data, cardActionSequenceRef.current + 1);
        if (nextDrawnCard) {
          drawnCard = nextDrawnCard;
          drawnCardSequence = nextDrawnCard.sequence;
        }
        return;
      }

      if (event === "hint_given") {
        if (typeof data.tokensLeft === "number") {
          setHints(data.tokensLeft);
        }
        setLastGameEventMessage("Hint sent.");
        return;
      }

      if (event === "hint_failed") {
        hasError = true;
        errorMessage = "Hint was not valid.";
        if (typeof data.tokensLeft === "number") {
          setHints(data.tokensLeft);
        }
        setGameActionError(errorMessage);
        return;
      }

      if (event === "misfire" && typeof data.misfire === "number") {
        setMisfires(data.misfire);
        return;
      }

      if (event === "turn_change" && typeof data.next_player === "string") {
        setActivePlayerName(data.next_player);
        return;
      }

      if (event === "game_over") {
        gameOverScore = typeof data.score === "number" ? data.score : null;
        setLastGameEventMessage(
          gameOverScore === null ? "Game over." : `Game over. Score: ${gameOverScore}`,
        );
      }
    });

    if (actionType && actionPlayerName && removedCardIndex !== null) {
      const nextSequence = drawnCardSequence ?? cardActionSequenceRef.current + 1;
      cardActionSequenceRef.current = nextSequence;
      cardAction = {
        actionType,
        drawnCard,
        playerName: actionPlayerName,
        removedCardIndex,
        sequence: nextSequence,
      };
      if (options.publishCardAction) {
        setLastCardAction(cardAction);
      }
    }

    return {
      cardAction,
      drawnCard,
      events,
      errorMessage,
      gameOverScore,
      hasError,
      hasGameState,
    };
  }, [applyGameStateFromEvents]);

  const loadLatestGameState = useCallback(async (client: HanabiWsClient) => {
    if (!routeGameId) {
      throw new Error("Missing game id.");
    }

    const events = await client.command<{ gameId: string; playerName: string | null }>("game.get_state", {
      gameId: routeGameId,
      playerName: getCurrentPlayerName(),
    });
    const error = getEventData<{ message?: string }>(events, "error");
    if (error) {
      throw new Error(error.message || "Unable to load game state.");
    }
    const hasGameState = applyGameStateFromEvents(events);
    if (!hasGameState) {
      throw new Error("Game state was not returned.");
    }

    return events;
  }, [applyGameStateFromEvents, routeGameId]);

  const refreshGameState = useCallback(async () => {
    const client = clientRef.current;
    if (!client) {
      return;
    }
    await loadLatestGameState(client);
  }, [loadLatestGameState]);

  useEffect(() => {
    const storedGameWsUrl = localStorage.getItem("hanabi.gameWsUrl");
    const gameId = routeGameId;

    if (!storedGameWsUrl || !gameId) {
      setGameSocketStatus("missing");
      return;
    }

    let isMounted = true;
    const client = new HanabiWsClient(storedGameWsUrl);
    clientRef.current = client;
    const unsubscribe = client.subscribe((events) => {
      const result = handleReturnedGameEvents(events, { publishCardAction: true });
      if (!result.hasError && !result.hasGameState && !result.cardAction) {
        void loadLatestGameState(client).catch((error) => {
          console.error("Failed to refresh game state after broadcast:", error);
          setGameSocketStatus("error");
        });
      }
    });

    setGameSocketUrl(storedGameWsUrl);
    setGameSocketStatus("connecting");

    void loadLatestGameState(client)
      .then(() => {
        if (!isMounted) {
          return;
        }
        setGameSocketStatus("connected");
      })
      .catch((error) => {
        if (!isMounted) {
          return;
        }
        console.error("Failed to load game state:", error);
        setGameSocketStatus("error");
      });

    return () => {
      isMounted = false;
      if (clientRef.current === client) {
        clientRef.current = null;
      }
      unsubscribe();
      client.close();
    };
  }, [handleReturnedGameEvents, loadLatestGameState, routeGameId]);

  const sendGameCommand = useCallback(async (
    action: string,
    data: Record<string, unknown>,
    options: { refreshAfter?: boolean } = {},
  ): Promise<GameCommandResult> => {
    const client = clientRef.current;
    if (!client || !routeGameId) {
      const message = "Game WebSocket is not ready.";
      setGameActionError(message);
      throw new Error(message);
    }

    setGameActionError("");

    let events: ServerEvent[];
    try {
      events = await client.command(action, {
        gameId: routeGameId,
        ...data,
      });
      const result = handleReturnedGameEvents(events);
      if (result.hasError) {
        throw new Error(result.errorMessage || "Game command failed.");
      }
      if (!result.hasGameState && options.refreshAfter !== false) {
        await loadLatestGameState(client);
      }

      return {
        cardAction: result.cardAction,
        drawnCard: result.drawnCard,
        events,
        gameOverScore: result.gameOverScore,
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : "Game command failed.";
      setGameActionError(message);
      throw error;
    }
  }, [handleReturnedGameEvents, loadLatestGameState, routeGameId]);

  const playCard = useCallback((playerName: string, cardIndex: number) => {
    return sendGameCommand("game.play_card", {
      playerId: playerName,
      cardIndex,
    }, { refreshAfter: false });
  }, [sendGameCommand]);

  const discardCard = useCallback((playerName: string, cardIndex: number) => {
    return sendGameCommand("game.discard_card", {
      playerId: playerName,
      cardIndex,
    }, { refreshAfter: false });
  }, [sendGameCommand]);

  const giveHint = useCallback((
    fromPlayerName: string,
    toPlayerName: string,
    hintType: "color" | "number",
    hintValue: CardColor | CardValue,
  ) => {
    return sendGameCommand("game.give_hint", {
      fromPlayerId: fromPlayerName,
      toPlayerId: toPlayerName,
      ...(hintType === "color"
        ? { color: COLOR_TO_BACKEND[hintValue as CardColor] }
        : { number: VALUE_TO_BACKEND[hintValue as CardValue] }),
    });
  }, [sendGameCommand]);

  return {
    activePlayerName,
    cardHintsByPlayer,
    deckCount,
    discardByColor,
    fireworkValues,
    gameActionError,
    gameSocketStatus,
    gameSocketUrl,
    handCardsByPlayer,
    hints,
    lastCardAction,
    lastGameEventMessage,
    misfires,
    players,
    discardCard,
    giveHint,
    playCard,
    refreshGameState,
    setCardHintsByPlayer,
    setHandCardsByPlayer,
  };
}
