"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { SETTINGS_NAV_ITEMS } from "./nav-config";
import { SettingsTopBar } from "./SettingsTopBar";

type Props = {
  children: React.ReactNode;
};

export function SettingsAppShell({ children }: Props) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-50">
      <SettingsTopBar />

      <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
        <div className="flex flex-col gap-8 lg:flex-row lg:items-start">
          <nav
            className="lg:w-64 lg:shrink-0"
            aria-label="Settings sections"
          >
            <div className="rounded-2xl border border-zinc-200 bg-white p-2 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
              <p className="hidden px-3 pb-2 pt-1 text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400 lg:block">
                Sections
              </p>
              <ul className="flex gap-2 overflow-x-auto pb-1 lg:flex-col lg:gap-1 lg:overflow-visible lg:pb-0">
                {SETTINGS_NAV_ITEMS.map((item) => {
                  const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
                  return (
                    <li key={item.href} className="shrink-0 lg:shrink">
                      <Link
                        href={item.href}
                        className={[
                          "block rounded-xl px-3 py-2.5 text-sm font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:focus-visible:outline-zinc-600",
                          active
                            ? "bg-zinc-900 text-white shadow-sm dark:bg-zinc-50 dark:text-zinc-900"
                            : "text-zinc-700 hover:bg-zinc-50 dark:text-zinc-200 dark:hover:bg-zinc-900",
                        ].join(" ")}
                        aria-current={active ? "page" : undefined}
                      >
                        <span className="block whitespace-nowrap">{item.label}</span>
                        <span className="mt-0.5 hidden text-xs font-normal opacity-80 lg:block">{item.description}</span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          </nav>

          <main className="min-w-0 flex-1 space-y-6">{children}</main>
        </div>
      </div>
    </div>
  );
}
