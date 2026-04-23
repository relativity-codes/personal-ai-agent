"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { PlanDetailView } from "./PlanDetailView";

export function PlanDetailRoute() {
  const searchParams = useSearchParams();
  const id = searchParams.get("id");

  if (!id) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          No plan selected. Open a plan from the{" "}
          <Link href="/plans" className="font-semibold text-zinc-900 underline-offset-4 hover:underline dark:text-zinc-50">
            plans list
          </Link>
          .
        </p>
      </div>
    );
  }

  return <PlanDetailView planId={id} />;
}
