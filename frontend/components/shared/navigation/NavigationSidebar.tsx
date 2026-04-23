"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { isMainNavActive, MAIN_NAV_ITEMS } from "@/lib/shared/main-nav";

export function NavigationSidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-full min-h-0 flex-col px-3 py-6">
      <Link
        href="/"
        className="mx-1 mb-8 inline-flex h-10 w-10 items-center justify-center rounded-xl border border-zinc-200 bg-zinc-50 text-xs font-bold tracking-tight text-zinc-900 shadow-sm transition hover:bg-zinc-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50 dark:hover:bg-zinc-800 dark:focus-visible:outline-zinc-600"
        aria-label="Personal AI Agent home"
      >
        PAI
      </Link>

      <nav aria-label="Main navigation">
        <ul className="space-y-1">
          {MAIN_NAV_ITEMS.map((item) => {
            const active = isMainNavActive(pathname, item.href);
            return (
              <li key={item.href}>
                <Link
                  href={item.href === "/settings" ? "/settings/profile" : item.href}
                  className={[
                    "block rounded-xl px-3 py-2.5 text-sm font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:focus-visible:outline-zinc-600",
                    active
                      ? "bg-zinc-900 text-white shadow-sm dark:bg-zinc-50 dark:text-zinc-900"
                      : "text-zinc-700 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-900",
                  ].join(" ")}
                  aria-current={active ? "page" : undefined}
                >
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </div>
  );
}
