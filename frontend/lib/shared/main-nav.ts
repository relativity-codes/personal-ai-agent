export type MainNavItem = {
  href: string;
  label: string;
};

/** §3.1 primary navigation (routes follow frontend-design inventory). */
export const MAIN_NAV_ITEMS: readonly MainNavItem[] = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/chat", label: "Chat" },
  { href: "/integrations", label: "Integrations" },
  { href: "/activity", label: "Activity" },
  { href: "/settings", label: "Settings" },
  { href: "/help", label: "Help" },
] as const;

export function isMainNavActive(pathname: string, href: string): boolean {
  if (href === "/dashboard") return pathname === "/dashboard";
  if (href === "/settings") return pathname === "/settings" || pathname.startsWith("/settings/");
  return pathname === href || pathname.startsWith(`${href}/`);
}
