import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-4 py-16 text-center">
      <p className="text-sm font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">404</p>
      <h1 className="mt-2 text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">Page not found</h1>
      <p className="mt-3 text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
        The link may be broken or the page was removed.
      </p>
      <Link
        href="/"
        className="mt-8 inline-flex min-h-[44px] items-center justify-center self-center rounded-lg bg-zinc-900 px-5 text-sm font-semibold text-white transition hover:bg-zinc-800 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
      >
        Go home
      </Link>
    </main>
  );
}
