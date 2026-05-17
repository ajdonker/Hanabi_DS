export type GameServerInfo = {
  game_id: string;
  host: string;
  port: number;
};

function getBackendHttpUrl(): string {
  const configured = (import.meta.env.VITE_BACKEND_HTTP_URL as string | undefined)?.trim();
  if (configured) {
    return configured.replace(/\/$/, "");
  }

  const websocketUrl = (import.meta.env.VITE_BACKEND_WS_URL as string | undefined)?.trim();
  if (websocketUrl) {
    return websocketUrl
      .replace(/^ws:/, "http:")
      .replace(/^wss:/, "https:")
      .replace(/\/ws$/, "");
  }

  return "http://localhost:8000";
}

export function toGameWsUrl(server: GameServerInfo): string {
  return `ws://${server.host}:${server.port}/ws`;
}

export async function resolveGameServer(gameId: string): Promise<GameServerInfo> {
  const response = await fetch(
    `${getBackendHttpUrl()}/games/${encodeURIComponent(gameId)}/server`,
  );

  if (!response.ok) {
    throw new Error("Unable to resolve game server.");
  }

  const data = await response.json() as Partial<GameServerInfo>;
  if (
    typeof data.game_id !== "string" ||
    typeof data.host !== "string" ||
    typeof data.port !== "number"
  ) {
    throw new Error("Game server response is invalid.");
  }

  return data as GameServerInfo;
}
