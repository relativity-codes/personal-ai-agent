import { getApiBaseUrl } from "@/lib/api/client";
import type { WsIncomingMessage } from "./types";

type ChatWebSocketOptions = {
  onStep: (step: Record<string, unknown>) => void;
  onFinalResponse: (message: string, sessionId: string) => void;
  onSessionCreated: (sessionId: string) => void;
  onError: (error: string) => void;
  onClose: () => void;
};

export class ChatWebSocket {
  private ws: WebSocket | null = null;
  private opts: ChatWebSocketOptions;

  constructor(opts: ChatWebSocketOptions) {
    this.opts = opts;
  }

  /** Resolves true when the socket is open, false on error or timeout. */
  connect(timeoutMs = 5000): Promise<boolean> {
    const base = getApiBaseUrl().replace(/^http/, "ws");
    const socket = new WebSocket(`${base}/ws/chat`);
    this.ws = socket;

    return new Promise((resolve) => {
      const timer = window.setTimeout(() => resolve(false), timeoutMs);

      const finish = (ok: boolean) => {
        window.clearTimeout(timer);
        resolve(ok);
      };

      socket.onopen = () => finish(true);

      socket.onerror = () => {
        this.opts.onError("WebSocket connection error");
        finish(false);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data as string) as WsIncomingMessage;
          if ("error" in data && typeof data.error === "string") {
            this.opts.onError(data.error);
          } else if ("type" in data && data.type === "session_created") {
            this.opts.onSessionCreated(data.session_id);
          } else if ("type" in data && data.type === "final_response") {
            this.opts.onFinalResponse(data.message, data.session_id);
          } else {
            this.opts.onStep(data as Record<string, unknown>);
          }
        } catch {
          // non-JSON frame — ignore
        }
      };

      socket.onclose = () => {
        this.opts.onClose();
      };
    });
  }

  send(message: string, sessionId?: string) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      this.opts.onError("WebSocket not connected");
      return;
    }
    this.ws.send(JSON.stringify({ message, session_id: sessionId ?? null }));
  }

  close() {
    this.ws?.close();
    this.ws = null;
  }

  get readyState() {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }
}

/** REST fallback for environments where WebSocket is unavailable. */
export async function sendMessageRest(
  message: string,
  sessionId?: string
): Promise<{ response: string; session_id: string }> {
  const body: { message: string; session_id?: string } = { message };
  if (sessionId) body.session_id = sessionId;

  const res = await fetch(`${getApiBaseUrl()}/api/v1/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Chat API error: ${res.status}`);
  return res.json() as Promise<{ response: string; session_id: string }>;
}
