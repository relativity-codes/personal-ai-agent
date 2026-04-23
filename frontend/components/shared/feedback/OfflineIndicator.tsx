"use client";

import { useOnlineStatus } from "./useOnlineStatus";

/** §3.4 Connection error — shown when the browser reports no network. */
export function OfflineIndicator() {
  const online = useOnlineStatus();
  if (online) return null;

  return (
    <div
      className="border-b border-amber-200 bg-amber-50 px-4 py-2 text-center text-sm font-medium text-amber-950 dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-100"
      role="status"
      aria-live="polite"
    >
      You&apos;re offline. Some actions may not work until you reconnect.
    </div>
  );
}
