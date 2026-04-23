import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Integrations",
  description: "Connect and manage MCP server integrations for Personal AI Agent.",
};

export default function IntegrationsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
