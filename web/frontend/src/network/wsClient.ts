export type ServerEvent = {
  event: string;
  data: Record<string, unknown>;
};

type EventBatchMessage = {
  type: "event_batch";
  events: ServerEvent[];
  requestId?: string;
};

type ErrorMessage = {
  type: "error";
  message: string;
  details?: Record<string, unknown>;
  requestId?: string;
};

type IncomingMessage = EventBatchMessage | ErrorMessage;

type PendingRequest = {
  resolve: (events: ServerEvent[]) => void;
  reject: (error: Error) => void;
  timer: number;
};

export type EventListener = (events: ServerEvent[]) => void;

type EndpointProvider = string | (() => string);

function getDefaultEndpoint(): string {
  const configured = (import.meta.env.VITE_BACKEND_WS_URL as string | undefined)?.trim();
  if (configured) {
    return configured;
  }
  return "ws://localhost:8000/ws";
}

export class HanabiWsClient {
  private socket: WebSocket | null = null;
  private connecting: Promise<WebSocket> | null = null;
  private pending = new Map<string, PendingRequest>();
  private listeners = new Set<EventListener>();

  constructor(private endpoint?: EndpointProvider) {}

  private getEndpoint(): string {
    if (typeof this.endpoint === "function") {
      return this.endpoint();
    }
    if (this.endpoint) {
      return this.endpoint;
    }
    return getDefaultEndpoint();
  }

  private async ensureConnection(): Promise<WebSocket> {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return this.socket;
    }
    if (this.connecting) {
      return this.connecting;
    }

    this.connecting = new Promise((resolve, reject) => {
      const socket = new WebSocket(this.getEndpoint());
      this.socket = socket;

      socket.onopen = () => {
        this.socket = socket;
        this.connecting = null;
        resolve(socket);
      };

      socket.onmessage = (event) => {
        this.handleMessage(event.data);
      };

      socket.onerror = () => {
        if (this.connecting) {
          this.connecting = null;
          reject(new Error("Unable to connect to backend WebSocket."));
        }
      };

      socket.onclose = () => {
        if (this.socket === socket) {
          this.socket = null;
        }
        if (this.connecting) {
          reject(new Error("WebSocket connection closed."));
        }
        this.connecting = null;
        this.rejectAllPending("WebSocket connection closed.");
      };
    });

    return this.connecting;
  }

  private handleMessage(rawData: unknown): void {
    if (typeof rawData !== "string") {
      return;
    }

    let envelope: IncomingMessage;
    try {
      envelope = JSON.parse(rawData) as IncomingMessage;
    } catch {
      return;
    }

    if (!envelope || typeof envelope !== "object" || !("type" in envelope)) {
      return;
    }

    if (envelope.type === "error") {
      this.handleError(envelope);
      return;
    }

    if (envelope.type !== "event_batch" || !Array.isArray(envelope.events)) {
      return;
    }

    this.emit(envelope.events);
    const requestId = envelope.requestId;
    if (!requestId) {
      return;
    }

    const pending = this.pending.get(requestId);
    if (!pending) {
      return;
    }

    window.clearTimeout(pending.timer);
    this.pending.delete(requestId);
    pending.resolve(envelope.events);
  }

  private handleError(message: ErrorMessage): void {
    const requestId = message.requestId;
    if (!requestId) {
      return;
    }
    const pending = this.pending.get(requestId);
    if (!pending) {
      return;
    }

    window.clearTimeout(pending.timer);
    this.pending.delete(requestId);
    pending.reject(new Error(message.message || "Request failed."));
  }

  private emit(events: ServerEvent[]): void {
    for (const listener of this.listeners) {
      listener(events);
    }
  }

  private rejectAllPending(message: string): void {
    for (const [, pending] of this.pending) {
      window.clearTimeout(pending.timer);
      pending.reject(new Error(message));
    }
    this.pending.clear();
  }

  subscribe(listener: EventListener): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  close(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.connecting = null;
    this.rejectAllPending("WebSocket connection closed.");
  }

  async command<TPayload = Record<string, unknown>>(
    action: string,
    data: TPayload,
    timeoutMs = 8000,
  ): Promise<ServerEvent[]> {
    const socket = await this.ensureConnection();
    const requestId = crypto.randomUUID();

    const promise = new Promise<ServerEvent[]>((resolve, reject) => {
      const timer = window.setTimeout(() => {
        this.pending.delete(requestId);
        reject(new Error("WebSocket request timed out."));
      }, timeoutMs);

      this.pending.set(requestId, {
        resolve,
        reject,
        timer,
      });
    });

    socket.send(
      JSON.stringify({
        type: "command",
        action,
        requestId,
        data,
      }),
    );

    return promise;
  }
}

export function getEventData<T>(events: ServerEvent[], eventName: string): T | null {
  const match = events.find((entry) => entry.event === eventName);
  if (!match || typeof match.data !== "object" || match.data === null) {
    return null;
  }
  return match.data as T;
}

export const wsClient = new HanabiWsClient();
