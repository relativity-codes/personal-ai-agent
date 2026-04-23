export type MessageRole = "user" | "assistant";

export type ChatMessage = {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
};

export type ChatSession = {
  session_id: string;
  messages: ChatMessage[];
};

export type WsIncomingMessage =
  | { type: "session_created"; session_id: string }
  | { type: "final_response"; message: string; session_id: string }
  | { type: "step"; [key: string]: unknown }
  | { error: string };
