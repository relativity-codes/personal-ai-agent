import Link from "next/link";

type Props = {
  userInitials?: string;
};

export function SettingsTopBar({ userInitials = "U" }: Props) {
  return (
    <header className="sticky top-0 z-30 border-b border-zinc-200/80 bg-white/80 backdrop-blur-md dark:border-zinc-800/80 dark:bg-zinc-950/70">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex min-w-0 items-center gap-3">
          <Link
            href="/"
            className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-zinc-200 bg-zinc-50 text-xs font-bold tracking-tight text-zinc-900 shadow-sm transition hover:bg-zinc-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50 dark:hover:bg-zinc-800 dark:focus-visible:outline-zinc-600"
            aria-label="Personal AI Agent home"
          >
            PAI
          </Link>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-zinc-900 dark:text-zinc-50">Settings</p>
            <p className="truncate text-xs text-zinc-500 dark:text-zinc-400 sm:hidden">Account & preferences</p>
          </div>
        </div>

        <button
          type="button"
          className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-zinc-200 bg-gradient-to-br from-zinc-50 to-zinc-200 text-sm font-semibold text-zinc-900 shadow-sm transition hover:from-white hover:to-zinc-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-800 dark:from-zinc-900 dark:to-zinc-950 dark:text-zinc-50 dark:hover:from-zinc-800 dark:hover:to-zinc-950 dark:focus-visible:outline-zinc-600"
          aria-label="Account menu (coming soon)"
        >
          <span aria-hidden>{userInitials}</span>
        </button>
      </div>
    </header>
  );
}
