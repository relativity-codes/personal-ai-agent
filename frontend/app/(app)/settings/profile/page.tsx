import type { Metadata } from "next";
import { ProfileSettingsView } from "@/components/settings/profile/ProfileSettingsView";

export const metadata: Metadata = {
  title: "Profile",
  description: "Update your avatar and personal information.",
};

export default function ProfileSettingsPage() {
  return <ProfileSettingsView />;
}
