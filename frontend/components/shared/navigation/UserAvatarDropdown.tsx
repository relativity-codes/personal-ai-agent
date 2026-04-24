"use client";

import { useAuth } from "@/lib/hooks/useAuth";
import { apiFetch } from "@/lib/api/client";
import { toast } from "sonner";
import { useEffect, useId, useRef, useState } from "react";
import Link from "next/link";

type MenuLink = { href: string; label: string };

const MENU_PRIMARY: MenuLink[] = [
  { href: "/settings/profile", label: "Profile" },
  { href: "/settings", label: "Settings" },
  { href: "/integrations", label: "Integrations" },
  { href: "/settings/tokens", label: "Usage stats" },
];

const MENU_SECONDARY: MenuLink[] = [
  { href: "/help", label: "Support" },
  { href: "/help", label: "Documentation" },
];

export function UserAvatarDropdown() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const buttonId = useId();
  const menuId = useId();

  const initials = user?.name
    ? user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
    : user?.email?.[0].toUpperCase() || "?";

  useEffect(() => {
    if (!open) return;

    function onPointerDown(e: PointerEvent) {
      const el = rootRef.current;
      if (!el) return;
      if (e.target instanceof Node && !el.contains(e.target)) setOpen(false);
    }

    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }

    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const handleLogout = async () => {
    try {
      await apiFetch("/api/v1/auth/logout", { method: "POST" });
      logout();
      setOpen(false);
      window.location.assign("/");
    } catch (err) {
      toast.error("Logout failed");
    }
  };

  if (!user) return null;

  return (
    <div ref={rootRef} className="relative">
      <button
        id={buttonId}
        type="button"
        className="inline-flex h-10 max-w-[min(100vw-8rem,220px)] items-center gap-2 rounded-full border border-zinc-200 bg-white py-1 pl-1 pr-2 text-left text-sm shadow-sm transition hover:bg-zinc-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-800 dark:bg-zinc-950 dark:hover:bg-zinc-900 dark:focus-visible:outline-zinc-600"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls={menuId}
        onClick={() => setOpen((v) => !v)}
      >
        {user.avatar_url ? (
          <img
            src={user.avatar_url}
            alt={user.name || "User"}
            className="h-8 w-8 rounded-full border border-zinc-100 object-cover shadow-sm dark:border-zinc-800"
          />
        ) : (
          <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-[11px] font-bold text-white shadow-sm">
            {initials}
          </span>
        )}
        <span className="hidden min-w-0 flex-1 sm:block">
          <span className="block truncate font-semibold text-zinc-900 dark:text-zinc-50">
            {user.name || "User"}
          </span>
          <span className="block truncate text-xs text-zinc-500 dark:text-zinc-400">
            {user.email}
          </span>
        </span>
      </button>

      {open ? (
        <div
          id={menuId}
          role="menu"
          aria-labelledby={buttonId}
          className="absolute right-0 z-50 mt-2 w-[min(calc(100vw-2rem),280px)] rounded-2xl border border-zinc-200 bg-white py-2 shadow-xl dark:border-zinc-800 dark:bg-zinc-950"
        >
          <div className="flex items-start gap-3 border-b border-zinc-100 px-4 pb-3 pt-2 sm:hidden dark:border-zinc-800">
            {user.avatar_url ? (
              <img
                src={user.avatar_url}
                alt={user.name || "User"}
                className="h-10 w-10 rounded-full border border-zinc-100 object-cover shadow-sm dark:border-zinc-800"
              />
            ) : (
              <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-sm font-bold text-white shadow-sm">
                {initials}
              </span>
            )}
            <div className="min-w-0">
              <p className="truncate font-semibold text-zinc-900 dark:text-zinc-50">
                {user.name || "User"}
              </p>
              <p className="truncate text-sm text-zinc-500 dark:text-zinc-400">
                {user.email}
              </p>
            </div>
          </div>

          <ul className="py-1">
            {MENU_PRIMARY.map((item) => (
              <li key={`${item.href}-${item.label}`}>
                <Link
                  role="menuitem"
                  href={item.href}
                  className="block px-4 py-2.5 text-sm font-medium text-zinc-800 hover:bg-zinc-50 dark:text-zinc-100 dark:hover:bg-zinc-900"
                  onClick={() => setOpen(false)}
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>

          <div className="my-1 border-t border-zinc-100 dark:border-zinc-800" />

          <ul className="py-1">
            {MENU_SECONDARY.map((item) => (
              <li key={`${item.href}-${item.label}`}>
                <Link
                  role="menuitem"
                  href={item.href}
                  className="block px-4 py-2.5 text-sm font-medium text-zinc-800 hover:bg-zinc-50 dark:text-zinc-100 dark:hover:bg-zinc-900"
                  onClick={() => setOpen(false)}
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>

          <div className="my-1 border-t border-zinc-100 dark:border-zinc-800" />

          <button
            type="button"
            role="menuitem"
            className="block w-full px-4 py-2.5 text-left text-sm font-semibold text-red-700 hover:bg-red-50 dark:text-red-300 dark:hover:bg-red-950/30"
            onClick={handleLogout}
          >
            Sign out
          </button>
        </div>
      ) : null}
    </div>
  );
}
