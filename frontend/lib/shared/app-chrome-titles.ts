/** Map URL → top bar title for the authenticated chrome. */
export function getMainAppTitle(pathname: string): string {
  if (pathname.startsWith("/settings")) return "Settings";
  if (pathname.startsWith("/integrations")) return "Integrations";
  if (pathname.startsWith("/chat")) return "Chat";
  if (pathname.startsWith("/plans")) return "Plans";
  if (pathname.startsWith("/activity")) return "Activity";
  if (pathname.startsWith("/help")) return "Help";
  if (pathname.startsWith("/dashboard")) return "Dashboard";
  return "Personal AI Agent";
}
