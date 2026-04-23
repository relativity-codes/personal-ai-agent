"use client";

import { useEffect, useRef } from "react";
import { MessageListSkeleton } from "@/components/shared/loading/MessageListSkeleton";
import type { ChatMessage } from "@/lib/chat/types";
import { AssistantMessage } from "./AssistantMessage";
import { TypingIndicator } from "./TypingIndicator";
import { UserMessage } from "./UserMessage";

type Props = {
  messages: ChatMessage[];
  typing: boolean;
  loading?: boolean;
};

export function MessageList({ messages, typing, loading }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  if (loading) return <MessageListSkeleton />;

  if (messages.length === 0 && !typing) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-2 px-4 py-16 text-center">
        <span className="text-4xl" aria-hidden>
          💬
        </span>
        <p className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">
          Start a conversation
        </p>
        <p className="max-w-xs text-xs text-zinc-400">
          Ask me to prepare your standup, review PRs, check your calendar, and more.
        </p>
      </div>
    );
  }

  return (
    <div
      className="flex-1 space-y-4 overflow-y-auto px-4 py-6"
      aria-live="polite"
      aria-label="Conversation"
    >
      {messages.map((msg) =>
        msg.role === "user" ? (
          <UserMessage key={msg.id} message={msg} />
        ) : (
          <AssistantMessage key={msg.id} message={msg} />
        )
      )}
      {typing && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  );
}
