"use client";

import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useChat } from "@/lib/hooks/useChat";
import { ChatInput } from "./ChatInput";
import { MessageList } from "./MessageList";
import { SuggestionsBar } from "./SuggestionsBar";

export function ChatInterface() {
  const searchParams = useSearchParams();
  const initialSessionId = searchParams.get("session_id") ?? undefined;
  const initialPrompt = searchParams.get("prompt") ?? undefined;

  const { messages, pending, typing, sendMessage } = useChat(initialSessionId);
  const [started, setStarted] = useState(false);

  // Auto-send preset prompt from Quick Actions
  useEffect(() => {
    if (initialPrompt && !started) {
      setStarted(true);
      sendMessage(initialPrompt);
    }
  }, [initialPrompt, started, sendMessage]);

  const handleSend = useCallback(
    (text: string) => {
      setStarted(true);
      sendMessage(text);
    },
    [sendMessage]
  );

  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col">
      <MessageList messages={messages} typing={typing} />

      <div className="shrink-0 border-t border-zinc-200 bg-white px-4 pb-4 pt-3 dark:border-zinc-800 dark:bg-zinc-950">
        {messages.length === 0 && !typing && (
          <div className="mb-3">
            <SuggestionsBar onSelect={handleSend} />
          </div>
        )}
        <ChatInput onSend={handleSend} disabled={pending} />
        <p className="mt-2 text-center text-xs text-zinc-400">
          Press{" "}
          <kbd className="rounded border border-zinc-200 px-1 font-mono dark:border-zinc-700">
            Enter
          </kbd>{" "}
          to send,{" "}
          <kbd className="rounded border border-zinc-200 px-1 font-mono dark:border-zinc-700">
            Shift+Enter
          </kbd>{" "}
          for new line
        </p>
      </div>
    </div>
  );
}
