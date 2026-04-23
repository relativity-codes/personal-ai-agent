import type { Metadata } from "next";
import { SettingsAppShell } from "@/components/settings";

export const metadata: Metadata = {
  title: "Settings",
  description: "Manage profile, preferences, and API tokens for Personal AI Agent.",
};

export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  return <SettingsAppShell>{children}</SettingsAppShell>;
}
