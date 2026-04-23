import Link from "next/link";

export function CTASection() {
  return (
    <section className="bg-zinc-900 py-16 dark:bg-zinc-50">
      <div className="mx-auto max-w-3xl px-4 text-center sm:px-6">
        <h2 className="text-2xl font-bold tracking-tight text-white dark:text-zinc-900 sm:text-3xl">
          Ready to automate your workflow?
        </h2>
        <p className="mt-4 text-sm leading-relaxed text-zinc-400 dark:text-zinc-600">
          Join developers using Personal AI Agent to stay on top of their tools without
          the context switching.
        </p>
        <Link
          href="/sign-in"
          className="mt-8 inline-block min-h-[44px] rounded-xl bg-white px-8 py-3 text-sm font-semibold text-zinc-900 shadow-sm transition hover:bg-zinc-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white dark:bg-zinc-900 dark:text-zinc-50 dark:hover:bg-zinc-800"
        >
          Get Started Free →
        </Link>
      </div>
    </section>
  );
}
