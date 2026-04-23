import type { Metadata } from "next";
import { PreferencesSettingsView } from "@/components/settings/preferences/PreferencesSettingsView";

export const metadata: Metadata = {
  title: "Preferences",
  description: "Configure defaults, working hours, notifications, and AI preferences.",
};

export default function PreferencesSettingsPage() {
  return <PreferencesSettingsView />;
}
