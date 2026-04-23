import type { ReactNode } from "react";
import type { ChatMessage } from "@/lib/chat/types";

function formatTime(date: Date) {
  return date.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

/** Minimal markdown: bold, inline code, code blocks, bullet lists. No deps. */
function renderMarkdown(text: string) {
  const lines = text.split("\n");
  const elements: ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Fenced code block
    if (line.startsWith("```")) {
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      elements.push(
        <pre
          key={i}
          className="my-2 overflow-x-auto rounded-xl bg-zinc-100 p-3 font-mono text-xs text-zinc-800 dark:bg-zinc-800 dark:text-zinc-200"
        >
          {codeLines.join("\n")}
        </pre>
      );
      i++;
      continue;
    }

    // Heading
    if (line.startsWith("## ")) {
      elements.push(
        <p key={i} className="mt-3 font-semibold text-zinc-900 dark:text-zinc-50">
          {line.slice(3)}
        </p>
      );
      i++;
      continue;
    }

    // Bullet
    if (line.startsWith("- ") || line.startsWith("* ")) {
      elements.push(
        <li key={i} className="ml-4 list-disc text-sm text-zinc-700 dark:text-zinc-300">
          {inlineMarkdown(line.slice(2))}
        </li>
      );
      i++;
      continue;
    }

    // Checkbox list
    if (line.startsWith("[ ] ") || line.startsWith("[x] ")) {
      const checked = line.startsWith("[x]");
      elements.push(
        <li key={i} className="ml-4 flex items-center gap-2 text-sm text-zinc-700 dark:text-zinc-300">
          <span aria-hidden>{checked ? "☑" : "☐"}</span>
          {line.slice(4)}
        </li>
      );
      i++;
      continue;
    }

    // Empty line
    if (line.trim() === "") {
      i++;
      continue;
    }

    // Normal paragraph
    elements.push(
      <p key={i} className="text-sm leading-relaxed text-zinc-700 dark:text-zinc-300">
        {inlineMarkdown(line)}
      </p>
    );
    i++;
  }

  return elements;
}

function inlineMarkdown(text: string): ReactNode {
  // bold **text** and inline `code`
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code
          key={i}
          className="rounded bg-zinc-100 px-1 font-mono text-xs text-zinc-800 dark:bg-zinc-800 dark:text-zinc-200"
        >
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}

type Props = { message: ChatMessage };

export function AssistantMessage({ message }: Props) {
  const isEmpty = !message.content;

  return (
    <div className="flex gap-3">
      <span className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-zinc-100 text-xs font-bold text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
        AI
      </span>
      <div className="max-w-[80%]">
        <div className="rounded-2xl rounded-tl-sm border border-zinc-200 bg-white px-4 py-3 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
          {isEmpty ? (
            <span className="text-sm text-zinc-400 italic">Thinking...</span>
          ) : (
            <div className="space-y-1">{renderMarkdown(message.content)}</div>
          )}
        </div>
        {!isEmpty && (
          <p className="mt-1 text-xs text-zinc-400">{formatTime(message.timestamp)}</p>
        )}
      </div>
    </div>
  );
}
