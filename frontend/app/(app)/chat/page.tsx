import type { Metadata } from "next";
import { Suspense } from "react";
import { ChatInterface } from "@/components/chat/ChatInterface";

export const metadata: Metadata = {
  title: "Chat",
  description: "Talk to your Personal AI Agent — it handles GitHub, Notion, Calendar, and Gmail.",
};

export default function ChatPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-sm text-zinc-500">Loading chat…</div>}>
      <ChatInterface />
    </Suspense>
  );
}
