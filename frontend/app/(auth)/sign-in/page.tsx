"use client";
import SignIn from "@/components/auth/SignIn";

export default function Page() {
  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-4 py-16">
      <div className="mt-3 flex flex-col items-center gap-4 text-sm text-zinc-600 dark:text-zinc-300">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          Sign in
        </h1>
        <SignIn />
      </div>
    </main>
  );
}
