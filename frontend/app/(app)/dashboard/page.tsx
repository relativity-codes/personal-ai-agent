import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Dashboard",
  description: "Overview, activity, and quick actions for Personal AI Agent.",
};

export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
        Dashboard content is a teammate-owned area. Shared navigation and layout are live — open{" "}
        <Link className="font-semibold text-zinc-900 underline-offset-4 hover:underline dark:text-zinc-50" href="/integrations">
          Integrations
        </Link>{" "}
        or{" "}
        <Link className="font-semibold text-zinc-900 underline-offset-4 hover:underline dark:text-zinc-50" href="/settings/profile">
          Settings
        </Link>{" "}
        to explore implemented pages.
      </p>
    </div>
  );
}
