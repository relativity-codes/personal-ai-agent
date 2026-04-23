/**
 * §3.4 Auth error handling — call when an API indicates the session is invalid.
 * Uses a full navigation so middleware / auth can run on the next load.
 */
export function redirectToSignIn(): void {
  if (typeof window === "undefined") return;
  window.location.assign("/sign-in");
}
