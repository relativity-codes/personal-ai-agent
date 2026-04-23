/** §3.3 Stats cards loading — placeholder number blocks. */
export function StatsCardSkeleton({ cards = 4 }: { cards?: number }) {
  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4" aria-busy="true" aria-live="polite">
      <p className="sr-only">Loading statistics</p>
      {Array.from({ length: cards }).map((_, i) => (
        <div
          key={i}
          className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
        >
          <div className="h-8 w-14 animate-pulse rounded-md bg-zinc-200 dark:bg-zinc-800" />
          <div className="mt-3 h-3 w-24 animate-pulse rounded bg-zinc-100 dark:bg-zinc-900" />
        </div>
      ))}
    </div>
  );
}
