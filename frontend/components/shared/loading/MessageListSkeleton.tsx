/** §3.3 Message list loading — stacked message-shaped skeletons. */
export function MessageListSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-4" aria-busy="true" aria-live="polite">
      <p className="sr-only">Loading messages</p>
      {Array.from({ length: rows }).map((_, i) => {
        const user = i % 2 === 0;
        return (
          <div key={i} className={`flex ${user ? "justify-end" : "justify-start"}`}>
            <div
              className={[
                "h-16 max-w-[min(100%,520px)] animate-pulse rounded-2xl border border-zinc-200 bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900",
                user ? "w-[min(92%,420px)]" : "w-[min(96%,560px)]",
              ].join(" ")}
            />
          </div>
        );
      })}
    </div>
  );
}
