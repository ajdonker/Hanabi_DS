import { useEffect, useState } from "react";
import { getEventData, HanabiWsClient } from "../network/wsClient";
import { colors } from "./config";
import type {
  CardColor,
  CardHintMarkers,
  CardValue,
  DiscardTableData,
  HandCard,
  Player,
} from "./types";

export type GameSocketStatus = "missing" | "connecting" | "connected" | "closed" | "error";

type BackendColor = "RED" | "YELLOW" | "GREEN" | "BLUE" | "WHITE";
type BackendNumber = "ONE" | "TWO" | "THREE" | "FOUR" | "FIVE";

type BackendHandCard = {
  number: BackendNumber;
  color: BackendColor;
  hints: {
    color: BackendColor | null;
    number: BackendNumber | null;
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
    piles: Record<BackendColor, number>;
    discards: Array<{
      number: BackendNumber;
      color: BackendColor;
    }>;
    tokens: number;
    misfires: number;
    deck_count: number;
  };
};

const COLOR_BY_BACKEND: Record<BackendColor, CardColor> = {
  RED: "Red",
  YELLOW: "Yellow",
  GREEN: "Green",
  BLUE: "Blue",
  WHITE: "White",
};

const BACKEND_COLOR_BY_FRONTEND: Record<CardColor, BackendColor> = {
  Red: "RED",
  Yellow: "YELLOW",
  Green: "GREEN",
  Blue: "BLUE",
  White: "WHITE",
};

const VALUE_BY_BACKEND: Record<BackendNumber, CardValue> = {
  ONE: 1,
  TWO: 2,
  THREE: 3,
  FOUR: 4,
  FIVE: 5,
};

function createPlaceholderHandsByPlayer(players: Player[]): Record<number, HandCard[]> {
  return {
    0: [
      { color: "Blue", value: 1 }
    ]
  };
}

function createEmptyDiscardByColor(): DiscardTableData {
  return colors.reduce<DiscardTableData>((discardByColor, color) => {
    discardByColor[color] = { 0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
    return discardByColor;
  }, {} as DiscardTableData);
}

function toFrontendCard(card: BackendHandCard): HandCard {
  return {
    color: COLOR_BY_BACKEND[card.color],
    value: VALUE_BY_BACKEND[card.number],
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
  const [fireworkValues, setFireworkValues] = useState<CardValue[]>([0, 0, 0, 0, 0]);
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

  useEffect(() => {
    const storedGameWsUrl = localStorage.getItem("hanabi.gameWsUrl");
    const currentPlayerName = localStorage.getItem("hanabi.username") ||
      localStorage.getItem("hanabi.playerId");
    const gameId = routeGameId;

    if (!storedGameWsUrl || !gameId) {
      setGameSocketStatus("missing");
      return;
    }

    let isMounted = true;
    const client = new HanabiWsClient(storedGameWsUrl);

    setGameSocketUrl(storedGameWsUrl);
    setGameSocketStatus("connecting");

    function applyGameState(gameState: BackendGameState) {
      console.log("Received game state:", gameState);
      const orderedBackendPlayers = rotatePlayersForCurrentUser(
        gameState.players,
        currentPlayerName,
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
            hintsForCard.colorHint = COLOR_BY_BACKEND[card.hints.color];
          }
          if (card.hints.number) {
            hintsForCard.numberHint = VALUE_BY_BACKEND[card.hints.number];
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
        const color = COLOR_BY_BACKEND[card.color];
        const value = VALUE_BY_BACKEND[card.number];
        nextDiscardByColor[color][value] += 1;
      });

      setPlayers(orderedPlayers);
      setHandCardsByPlayer(nextHandsByPlayer);
      setCardHintsByPlayer(nextHintsByPlayer);
      setFireworkValues(
        colors.map((color) => {
          const backendColor = BACKEND_COLOR_BY_FRONTEND[color];
          const pileValue = gameState.board.piles[backendColor] ?? 0;
          return Math.max(0, Math.min(5, pileValue)) as CardValue;
        }),
      );
      setDiscardByColor(nextDiscardByColor);
      setHints(gameState.board.tokens);
      setMisfires(gameState.board.misfires);
      setDeckCount(gameState.board.deck_count);
      setActivePlayerName(gameState.player_turn);
    }

    void client
      .command<{ gameId: string }>("game.get_state", { gameId })
      .then((events) => {
        if (!isMounted) {
          return;
        }
        const gameState = getEventData<BackendGameState>(events, "game_state");
        if (!gameState) {
          setGameSocketStatus("error");
          return;
        }
        applyGameState(gameState);
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
      client.close();
    };
  }, [routeGameId]);

  return {
    activePlayerName,
    cardHintsByPlayer,
    deckCount,
    discardByColor,
    fireworkValues,
    gameSocketStatus,
    gameSocketUrl,
    handCardsByPlayer,
    hints,
    misfires,
    players,
    setCardHintsByPlayer,
    setHandCardsByPlayer,
  };
}
