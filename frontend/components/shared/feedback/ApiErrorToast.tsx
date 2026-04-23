"use client";

type Props = {
  open: boolean;
  message: string;
  onRetry?: () => void;
  onDismiss: () => void;
};

/** §3.4 API error — fixed toast with optional retry. */
export function ApiErrorToast({ open, message, onRetry, onDismiss }: Props) {
  if (!open) return null;

  return (
    <div
      className="fixed bottom-[calc(5.5rem+env(safe-area-inset-bottom))] left-4 right-4 z-[60] sm:left-auto sm:right-4 sm:w-[min(100vw-2rem,400px)] lg:bottom-6"
      role="alert"
    >
      <div className="rounded-2xl border border-red-200 bg-white p-4 shadow-xl dark:border-red-900/50 dark:bg-zinc-950">
        <div className="flex items-start justify-between gap-3">
          <p className="text-sm font-medium text-red-950 dark:text-red-100">{message}</p>
          <button
            type="button"
            className="rounded-lg p-1 text-red-700 transition hover:bg-red-50 dark:text-red-300 dark:hover:bg-red-950/40"
            onClick={onDismiss}
            aria-label="Dismiss error"
          >
            <span aria-hidden>×</span>
          </button>
        </div>
        {onRetry ? (
          <div className="mt-3">
            <button
              type="button"
              className="inline-flex min-h-[40px] w-full items-center justify-center rounded-lg bg-red-700 px-3 text-sm font-semibold text-white transition hover:bg-red-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-700 dark:bg-red-600 dark:hover:bg-red-500 sm:w-auto"
              onClick={onRetry}
            >
              Retry
            </button>
          </div>
        ) : null}
      </div>
    </div>
  );
}
