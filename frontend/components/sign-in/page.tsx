import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Sign in",
  description: "Sign in to Personal AI Agent.",
};

export default function SignInPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-4 py-16">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
        Sign in
      </h1>
      <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-300">
        Authentication UI is not wired yet. This route exists so auth error
        handlers can redirect here (§3.4).
      </p>
      <Link
        href="/dashboard"
        className="mt-8 inline-flex min-h-[44px] items-center justify-center rounded-lg bg-zinc-900 px-4 text-sm font-semibold text-white dark:bg-zinc-50 dark:text-zinc-900"
      >
        Back to app
      </Link>
    </main>
  );
}
