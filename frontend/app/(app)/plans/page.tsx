import type { Metadata } from "next";
import { PlansView } from "@/components/plans/PlansView";

export const metadata: Metadata = {
  title: "Plans",
  description: "View execution plan history — all your AI agent runs in one place.",
};

export default function PlansPage() {
  return <PlansView />;
}
