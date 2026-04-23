"use client";

import { useEffect, useRef, useState } from "react";

const DEMO_STEPS = [
  { role: "user", text: "Prepare for tomorrow's standup" },
  { role: "agent", text: "Fetching your calendar events..." },
  { role: "agent", text: "Listing open pull requests on GitHub..." },
  { role: "agent", text: "Creating standup agenda in Notion..." },
  {
    role: "agent",
    text: "Done! Your standup agenda is ready:\n• Sprint Planning at 10 AM\n• 2 PRs need review (#245, #247)\n• Agenda created in Notion →",
  },
];

/** Strict height: outer frame must not grow with message content (scroll happens inside). */
const DEMO_FRAME_HEIGHT = "h-[26rem] max-h-[80vh] shrink-0 overflow-hidden sm:h-[28rem]";

export function DemoAnimation() {
  const [visibleCount, setVisibleCount] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (visibleCount >= DEMO_STEPS.length) return;
    const delay = visibleCount === 0 ? 800 : 1400;
    const t = setTimeout(() => setVisibleCount((c) => c + 1), delay);
    return () => clearTimeout(t);
  }, [visibleCount]);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [visibleCount]);

  return (
    <section className="bg-zinc-50 py-16 dark:bg-zinc-900/50">
      <div className="mx-auto max-w-4xl px-4 sm:px-6">
        <h2 className="mb-2 text-center text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
          See it in action
        </h2>
        <p className="mb-10 text-center text-sm text-zinc-600 dark:text-zinc-400">
          One request, multiple tools — all handled automatically.
        </p>

        <div
          className={`flex min-h-0 flex-col rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-950 ${DEMO_FRAME_HEIGHT}`}
        >
          <div className="mb-3 shrink-0 flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-red-400" aria-hidden />
            <span className="h-3 w-3 rounded-full bg-yellow-400" aria-hidden />
            <span className="h-3 w-3 rounded-full bg-green-400" aria-hidden />
            <span className="ml-2 text-xs text-zinc-400">Personal AI Agent</span>
          </div>

          <div
            ref={scrollRef}
            className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden pr-1 font-mono text-sm [scrollbar-gutter:stable]"
            aria-live="polite"
          >
            <div className="space-y-3">
              {DEMO_STEPS.slice(0, visibleCount).map((step, i) => (
                <div
                  key={i}
                  className={[
                    "flex gap-3",
                    step.role === "user" ? "justify-end" : "justify-start",
                  ].join(" ")}
                >
                  {step.role === "agent" && (
                    <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-zinc-100 text-xs dark:bg-zinc-800">
                      AI
                    </span>
                  )}
                  <div
                    className={[
                      "max-w-[min(100%,18rem)] rounded-xl px-3 py-2 text-xs leading-relaxed whitespace-pre-line sm:max-w-xs",
                      step.role === "user"
                        ? "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900"
                        : "border border-zinc-200 bg-zinc-50 text-zinc-800 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200",
                    ].join(" ")}
                  >
                    {step.text}
                  </div>
                </div>
              ))}

              {visibleCount < DEMO_STEPS.length && (
                <div className="flex gap-3">
                  <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-zinc-100 text-xs dark:bg-zinc-800">
                    AI
                  </span>
                  <div className="flex items-center gap-1 rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900">
                    {[0, 1, 2].map((i) => (
                      <span
                        key={i}
                        className="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-400"
                        style={{ animationDelay: `${i * 150}ms` }}
                        aria-hidden
                      />
                    ))}
                  </div>
                </div>
              )}

              {visibleCount >= DEMO_STEPS.length && (
                <button
                  type="button"
                  onClick={() => setVisibleCount(0)}
                  className="text-left text-xs text-zinc-400 underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400"
                >
                  Replay demo
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
