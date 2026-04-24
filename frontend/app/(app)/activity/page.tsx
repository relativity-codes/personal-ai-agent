import type { Metadata } from "next";
import { ActivityList } from "@/components/activity/ActivityList";

export const metadata: Metadata = {
  title: "Activity",
  description: "Your conversation history and AI agent activities.",
};

export default function ActivityPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <header className="mb-10">
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">Activity Feed</h1>
        <p className="mt-2 text-zinc-500 dark:text-zinc-400">
          A log of your recent interactions and tasks performed by your AI agent.
        </p>
      </header>

      <ActivityList />
    </div>
  );
}
