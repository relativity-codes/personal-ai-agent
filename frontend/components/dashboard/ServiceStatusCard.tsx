import Link from "next/link";
import type { McpServer } from "@/lib/dashboard/types";

const LABELS: Record<string, string> = {
  github: "GitHub",
  notion: "Notion",
  calendar: "Calendar",
  gmail: "Gmail",
};

type Props = { server: McpServer };

export function ServiceStatusCard({ server }: Props) {
  const label = LABELS[server.name] ?? server.name;
  return (
    <div className="flex items-center justify-between rounded-2xl border border-zinc-200 bg-white p-3 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
      <span className="text-sm font-semibold text-zinc-800 dark:text-zinc-200">{label}</span>
      {server.configured ? (
        <span className="flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-semibold text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" aria-hidden />
          Connected
        </span>
      ) : (
        <Link
          href="/integrations"
          className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-semibold text-zinc-500 transition hover:bg-zinc-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:bg-zinc-700"
        >
          Connect →
        </Link>
      )}
    </div>
  );
}
