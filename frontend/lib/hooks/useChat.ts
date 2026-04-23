"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ChatWebSocket, sendMessageRest } from "@/lib/chat/websocket";
import type { ChatMessage } from "@/lib/chat/types";

let _msgId = 0;
function nextId() {
  return String(++_msgId);
}

export function useChat(initialSessionId?: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | undefined>(initialSessionId);
  const [pending, setPending] = useState(false);
  const [typing, setTyping] = useState(false);
  const wsRef = useRef<ChatWebSocket | null>(null);
  const assistantIdRef = useRef<string | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const ws = new ChatWebSocket({
      onSessionCreated: (sid) => setSessionId(sid),
      onStep: () => setTyping(true),
      onFinalResponse: (message, sid) => {
        setSessionId(sid);
        setTyping(false);
        setPending(false);
        const id = assistantIdRef.current;
        if (id) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === id ? { ...m, content: message, timestamp: new Date() } : m
            )
          );
          assistantIdRef.current = null;
        } else {
          setMessages((prev) => [
            ...prev,
            { id: nextId(), role: "assistant", content: message, timestamp: new Date() },
          ]);
        }
      },
      onError: (err) => {
        console.warn("Chat WS:", err);
        setTyping(false);
        setPending(false);
        const id = assistantIdRef.current;
        if (id) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === id
                ? {
                    ...m,
                    content: `Something went wrong: ${err}`,
                    timestamp: new Date(),
                  }
                : m
            )
          );
          assistantIdRef.current = null;
        }
      },
      onClose: () => {
        setTyping(false);
      },
    });

    let cancelled = false;
    void ws.connect().then((ok) => {
      if (!cancelled && ok) wsRef.current = ws;
    });

    return () => {
      cancelled = true;
      ws.close();
      wsRef.current = null;
    };
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || pending) return;

      const userMsg: ChatMessage = {
        id: nextId(),
        role: "user",
        content: text,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setPending(true);

      const placeholderId = nextId();
      assistantIdRef.current = placeholderId;
      setMessages((prev) => [
        ...prev,
        { id: placeholderId, role: "assistant", content: "", timestamp: new Date() },
      ]);

      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        setTyping(true);
        ws.send(text, sessionId);
        return;
      }

      try {
        const result = await sendMessageRest(text, sessionId);
        setSessionId(result.session_id);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === placeholderId
              ? { ...m, content: result.response, timestamp: new Date() }
              : m
          )
        );
        assistantIdRef.current = null;
      } catch {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === placeholderId
              ? {
                  ...m,
                  content: "Sorry, something went wrong. Please try again.",
                  timestamp: new Date(),
                }
              : m
          )
        );
        assistantIdRef.current = null;
      } finally {
        setPending(false);
        setTyping(false);
      }
    },
    [pending, sessionId]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setSessionId(undefined);
  }, []);

  return { messages, sessionId, pending, typing, sendMessage, clearMessages };
}
