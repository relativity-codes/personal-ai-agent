import type { Metadata } from "next";
import { Suspense } from "react";
import { PlanDetailRoute } from "@/components/plans/PlanDetailRoute";

export const metadata: Metadata = {
  title: "Plan details",
  description: "Detailed execution view for a plan.",
};

export default function PlanDetailPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-sm text-zinc-500">Loading plan…</div>}>
      <PlanDetailRoute />
    </Suspense>
  );
}
