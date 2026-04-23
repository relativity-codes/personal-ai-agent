type Props = {
  configured: boolean;
};

export function ConnectionStatusBadge({ configured }: Props) {
  return (
    <div
      className="inline-flex items-center gap-2 text-sm font-medium text-zinc-700 dark:text-zinc-200"
      role="status"
      aria-live="polite"
    >
      <span
        className={[
          "inline-flex h-2.5 w-2.5 shrink-0 rounded-full",
          configured ? "bg-emerald-500 shadow-[0_0_0_3px_rgba(16,185,129,0.25)]" : "border-2 border-zinc-400 bg-transparent dark:border-zinc-500",
        ].join(" ")}
        aria-hidden
      />
      <span>{configured ? "Configured" : "Not configured"}</span>
    </div>
  );
}
