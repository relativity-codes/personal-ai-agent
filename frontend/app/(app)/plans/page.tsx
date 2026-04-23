import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Plans",
  description: "View execution plans history.",
};

export default function PlansPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
        Plans list and filters will live here per the product spec.
      </p>
    </div>
  );
}
