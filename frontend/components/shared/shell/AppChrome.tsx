"use client";

import Link from "next/link";
import { useMemo } from "react";
import { usePathname } from "next/navigation";
import { getMainAppTitle } from "@/lib/shared/app-chrome-titles";
import { AppBottomNav } from "../navigation/AppBottomNav";
import { NavigationSidebar } from "../navigation/NavigationSidebar";
import { UserAvatarDropdown } from "../navigation/UserAvatarDropdown";
import { OfflineIndicator } from "../feedback/OfflineIndicator";

type Props = {
  children: React.ReactNode;
};

export function AppChrome({ children }: Props) {
  const pathname = usePathname();
  const title = useMemo(() => getMainAppTitle(pathname), [pathname]);

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-50">
      <div className="flex min-h-screen">
        <aside className="hidden w-56 shrink-0 border-r border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950 lg:block">
          <NavigationSidebar />
        </aside>

        <div className="flex min-h-0 min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-30 flex h-14 shrink-0 items-center gap-3 border-b border-zinc-200/80 bg-white/90 px-3 backdrop-blur-md dark:border-zinc-800/80 dark:bg-zinc-950/90 sm:px-4">
            <Link
              href="/"
              className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-zinc-200 bg-zinc-50 text-xs font-bold tracking-tight text-zinc-900 shadow-sm transition hover:bg-zinc-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50 dark:hover:bg-zinc-800 dark:focus-visible:outline-zinc-600 lg:hidden"
              aria-label="Personal AI Agent home"
            >
              PAI
            </Link>
            <div className="flex min-w-0 flex-1 items-center justify-between gap-3">
              <h1 className="truncate text-sm font-semibold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-base">
                {title}
              </h1>
              <UserAvatarDropdown />
            </div>
          </header>

          <OfflineIndicator />

          <div className="flex-1 pb-[calc(5.5rem+env(safe-area-inset-bottom))] lg:pb-0">{children}</div>
        </div>
      </div>

      <AppBottomNav />
    </div>
  );
}
