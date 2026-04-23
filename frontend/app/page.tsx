import type { Metadata } from "next";
import { CTASection } from "@/components/landing/CTASection";
import { DemoAnimation } from "@/components/landing/DemoAnimation";
import { FeatureCard } from "@/components/landing/FeatureCard";
import { Footer } from "@/components/landing/Footer";
import { HeroSection } from "@/components/landing/HeroSection";
import { IntegrationLogoGrid } from "@/components/landing/IntegrationLogoGrid";
import { NavigationBar } from "@/components/landing/NavigationBar";

export const metadata: Metadata = {
  title: "Personal AI Agent — Your AI Assistant That Actually Does Things",
  description:
    "Connect GitHub, Notion, Calendar, and Gmail. Ask in plain English — your AI agent plans and executes tasks across all your tools.",
};

const FEATURES = [
  {
    icon: "💬",
    title: "Natural Language",
    description:
      'Just say "Show me my PRs" or "Prepare for standup" — no commands to memorise.',
  },
  {
    icon: "⚡",
    title: "Multi-Tool Actions",
    description:
      "GitHub, Notion, Calendar, and Gmail all work together in a single request.",
  },
  {
    icon: "📡",
    title: "Real-Time Streaming",
    description:
      "Watch your agent work step-by-step with live streaming responses.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white text-zinc-900 dark:bg-zinc-950 dark:text-zinc-50">
      <NavigationBar />
      <main>
        <HeroSection />

        <section className="mx-auto max-w-4xl px-4 pb-16 sm:px-6">
          <h2 className="mb-8 text-center text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
            Everything you need to move faster
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {FEATURES.map((f) => (
              <FeatureCard key={f.title} {...f} />
            ))}
          </div>
        </section>

        <DemoAnimation />
        <IntegrationLogoGrid />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
}
