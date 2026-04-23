"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { isMainNavActive, MAIN_NAV_ITEMS } from "@/lib/shared/main-nav";

export function AppBottomNav() {
  const pathname = usePathname();

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-40 border-t border-zinc-200 bg-white/95 pb-[calc(0.5rem+env(safe-area-inset-bottom))] pt-2 shadow-[0_-8px_24px_rgba(0,0,0,0.06)] backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-950/95 lg:hidden"
      aria-label="Main navigation"
    >
      <ul className="flex gap-1 overflow-x-auto px-2 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {MAIN_NAV_ITEMS.map((item) => {
          const active = isMainNavActive(pathname, item.href);
          const href = item.href === "/settings" ? "/settings/profile" : item.href;
          return (
            <li key={item.href} className="shrink-0">
              <Link
                href={href}
                className={[
                  "flex min-h-[44px] min-w-[4.25rem] max-w-[5.5rem] flex-col items-center justify-center rounded-xl px-2 py-1.5 text-center text-[11px] font-semibold leading-tight transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:focus-visible:outline-zinc-600",
                  active
                    ? "text-zinc-900 dark:text-zinc-50"
                    : "text-zinc-500 hover:text-zinc-800 dark:text-zinc-400 dark:hover:text-zinc-100",
                ].join(" ")}
                aria-current={active ? "page" : undefined}
              >
                <span className="line-clamp-2">{item.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
