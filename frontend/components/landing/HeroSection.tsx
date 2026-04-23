import Link from "next/link";

export function HeroSection() {
  return (
    <section className="mx-auto max-w-4xl px-4 py-20 text-center sm:px-6 sm:py-28">
      <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-zinc-200 bg-zinc-50 px-3 py-1 text-xs font-medium text-zinc-600 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-400">
        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" aria-hidden />
        Now in early access
      </div>

      <h1 className="mt-6 text-4xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-5xl lg:text-6xl">
        Your Personal AI Assistant
        <br />
        <span className="text-zinc-500">That Actually Does Things</span>
      </h1>

      <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-zinc-600 dark:text-zinc-400">
        Connect GitHub, Notion, Calendar, and Gmail. Then just ask — your AI agent
        plans and executes tasks across all your tools automatically.
      </p>

      <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
        <Link
          href="/sign-in"
          className="min-h-[44px] rounded-xl bg-zinc-900 px-8 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-zinc-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
        >
          Get Started — It&apos;s Free →
        </Link>
        <Link
          href="/sign-in"
          className="min-h-[44px] rounded-xl px-8 py-3 text-sm font-semibold text-zinc-700 transition hover:bg-zinc-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:text-zinc-200 dark:hover:bg-zinc-900"
        >
          Sign In
        </Link>
      </div>

      <p className="mt-8 text-sm italic text-zinc-500 dark:text-zinc-500">
        &ldquo;Prepare for tomorrow&apos;s standup&rdquo; — and it just works.
      </p>
    </section>
  );
}
