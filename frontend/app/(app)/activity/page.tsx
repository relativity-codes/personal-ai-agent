import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Activity",
  description: "User activity log.",
};

export default function ActivityPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
        Activity feed will connect to <code className="rounded bg-zinc-100 px-1 py-0.5 text-xs dark:bg-zinc-900">/api/v1/activity</code> when available.
      </p>
    </div>
  );
}
