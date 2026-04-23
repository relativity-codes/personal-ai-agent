import type { Metadata } from "next";
import { TokensSettingsView } from "@/components/settings/tokens/TokensSettingsView";

export const metadata: Metadata = {
  title: "API Tokens",
  description: "Manage API tokens, view usage statistics, and delete your account.",
};

export default function TokensSettingsPage() {
  return <TokensSettingsView />;
}
