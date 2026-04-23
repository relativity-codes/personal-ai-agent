import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Chat",
  description: "Main AI interaction interface.",
};

export default function ChatPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
        Chat UI will be implemented in the chat feature track. Navigation shell is shared (§3).
      </p>
    </div>
  );
}
