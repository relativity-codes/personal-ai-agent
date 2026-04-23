"use client";

import { useState } from "react";

type Props = { data: unknown; label?: string };

export function RawJsonViewer({ data, label = "View Full JSON Response" }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between gap-3 p-5 text-left text-sm font-semibold text-zinc-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:text-zinc-200"
        aria-expanded={open}
      >
        <span>{label}</span>
        <span className="text-xs text-zinc-400">{open ? "▲ Hide" : "▼ Show"}</span>
      </button>
      {open && (
        <div className="border-t border-zinc-100 p-5 dark:border-zinc-800">
          <pre className="overflow-x-auto rounded-xl bg-zinc-50 p-4 font-mono text-xs leading-relaxed text-zinc-800 dark:bg-zinc-900 dark:text-zinc-200">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
