"use client";

type Props = {
  retryAfterSeconds: number;
  onDismiss?: () => void;
};

/** §3.4 Rate limit — full-width dismissible banner with wait hint. */
export function RateLimitBanner({ retryAfterSeconds, onDismiss }: Props) {
  const label =
    retryAfterSeconds >= 60
      ? `${Math.ceil(retryAfterSeconds / 60)} min`
      : `${Math.max(1, Math.ceil(retryAfterSeconds))} sec`;

  return (
    <div
      className="flex flex-col gap-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950 shadow-sm dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-100 sm:flex-row sm:items-center sm:justify-between"
      role="status"
    >
      <p className="font-medium">
        Rate limited. Please try again in about <span className="whitespace-nowrap">{label}</span>.
      </p>
      {onDismiss ? (
        <button
          type="button"
          className="inline-flex min-h-[40px] shrink-0 items-center justify-center rounded-lg border border-amber-300 bg-white px-3 text-sm font-semibold text-amber-950 transition hover:bg-amber-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-600 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-50 dark:hover:bg-amber-900/40 dark:focus-visible:outline-amber-500"
          onClick={onDismiss}
        >
          Dismiss
        </button>
      ) : null}
    </div>
  );
}
