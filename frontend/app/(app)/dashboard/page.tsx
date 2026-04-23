import type { Metadata } from "next";
import { DashboardView } from "@/components/dashboard/DashboardView";

export const metadata: Metadata = {
  title: "Dashboard",
  description: "Overview, activity, and quick actions for Personal AI Agent.",
};

export default function DashboardPage() {
  return <DashboardView />;
}
