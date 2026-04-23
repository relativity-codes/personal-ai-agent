import type { ChatMessage } from "@/lib/chat/types";

function formatTime(date: Date) {
  return date.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

type Props = { message: ChatMessage };

export function UserMessage({ message }: Props) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[75%]">
        <div className="rounded-2xl rounded-tr-sm bg-zinc-900 px-4 py-3 text-sm leading-relaxed text-white dark:bg-zinc-100 dark:text-zinc-900">
          {message.content}
        </div>
        <p className="mt-1 text-right text-xs text-zinc-400">
          {formatTime(message.timestamp)}
        </p>
      </div>
    </div>
  );
}
