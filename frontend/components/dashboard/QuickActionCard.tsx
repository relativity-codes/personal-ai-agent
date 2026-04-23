import Link from "next/link";

type Props = {
  icon: string;
  label: string;
  prompt: string;
};

export function QuickActionCard({ icon, label, prompt }: Props) {
  const href = `/chat?prompt=${encodeURIComponent(prompt)}`;
  return (
    <Link
      href={href}
      className="flex min-h-[44px] items-center gap-3 rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm transition hover:border-zinc-300 hover:shadow-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-800 dark:bg-zinc-950 dark:hover:border-zinc-700"
    >
      <span
        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-zinc-100 text-lg dark:bg-zinc-900"
        aria-hidden
      >
        {icon}
      </span>
      <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">{label}</span>
      <span className="ml-auto text-xs text-zinc-400" aria-hidden>
        →
      </span>
    </Link>
  );
}
