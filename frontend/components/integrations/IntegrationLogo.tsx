import type { IntegrationId } from "@/lib/integrations/types";

type Props = {
  id: IntegrationId;
  className?: string;
};

export function IntegrationLogo({ id, className }: Props) {
  const common = "h-10 w-10 shrink-0 rounded-xl border border-zinc-200 bg-white p-2 text-zinc-900 shadow-sm dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50";

  switch (id) {
    case "github":
      return (
        <div className={`${common} ${className ?? ""}`} aria-hidden>
          <svg viewBox="0 0 24 24" className="h-full w-full" fill="currentColor">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
          </svg>
        </div>
      );
    case "notion":
      return (
        <div className={`${common} ${className ?? ""}`} aria-hidden>
          <svg viewBox="0 0 24 24" className="h-full w-full" fill="currentColor">
            <path d="M4.5 3.75h15v1.5h-15v-1.5Zm0 4.5h10.5v1.5H4.5v-1.5Zm0 4.5h12v1.5h-12v-1.5Zm0 4.5h9v1.5h-9v-1.5Z" />
          </svg>
        </div>
      );
    case "calendar":
      return (
        <div className={`${common} ${className ?? ""}`} aria-hidden>
          <svg viewBox="0 0 24 24" className="h-full w-full">
            <path
              fill="#1a73e8"
              d="M17 3h-1V1h-2v2H10V1H8v2H7a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V6a3 3 0 0 0-3-3Zm1 15a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V9h12v9Z"
            />
            <path fill="#fff" d="M7 9h10v2H7V9Zm0 4h4v3H7v-3Zm6 0h4v3h-4v-3ZM7 17h4v2H7v-2Zm6 0h4v2h-4v-2Z" />
          </svg>
        </div>
      );
    case "gmail":
      return (
        <div className={`${common} ${className ?? ""}`} aria-hidden>
          <svg viewBox="0 0 24 24" className="h-full w-full">
            <path fill="#EA4335" d="M3 6.5 12 13l9-6.5V6l-9 6.5L3 6v.5Z" />
            <path fill="#FBBC04" d="M21 6.5V18l-6-4.5V9.2L21 6.5Z" />
            <path fill="#34A853" d="M21 18H3V6.5l9 6.5 9-6.5V18Z" />
            <path fill="#C5221F" d="M3 18V6.5L9 9.2v4.3L3 18Z" />
          </svg>
        </div>
      );
    default:
      return null;
  }
}
