import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Help",
  description: "Documentation and support.",
};

export default function HelpPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
        Public help and documentation pages can replace this placeholder.
      </p>
    </div>
  );
}
