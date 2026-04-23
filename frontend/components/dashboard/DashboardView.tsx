"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { StatsCardSkeleton } from "@/components/shared/loading/StatsCardSkeleton";
import { PlanCardSkeleton } from "@/components/shared/loading/PlanCardSkeleton";
import {
  fetchDashboardStats,
  fetchMcpServers,
  fetchRecentActivity,
  fetchRecentPlans,
} from "@/lib/dashboard/api";
import type {
  ActivityItem,
  DashboardStats,
  McpServer,
  RecentPlan,
} from "@/lib/dashboard/types";
import { ActivityList } from "./ActivityList";
import { QuickActionCard } from "./QuickActionCard";
import { RecentPlansList } from "./RecentPlansList";
import { ServiceStatusCard } from "./ServiceStatusCard";
import { StatsCard } from "./StatsCard";

const QUICK_ACTIONS = [
  { icon: "💬", label: "New Chat", prompt: "Hello" },
  { icon: "📋", label: "Standup Prep", prompt: "Prepare for tomorrow's standup" },
  { icon: "🔀", label: "PR Review", prompt: "List my open pull requests" },
  { icon: "📅", label: "My Week", prompt: "Summarize my week" },
];

export function DashboardView() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [plans, setPlans] = useState<RecentPlan[]>([]);
  const [servers, setServers] = useState<McpServer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [s, a, p, srv] = await Promise.all([
        fetchDashboardStats(),
        fetchRecentActivity(5),
        fetchRecentPlans(5),
        fetchMcpServers(),
      ]);
      setStats(s);
      setActivity(a);
      setPlans(p);
      setServers(srv);
      setLoading(false);
    }
    load();
  }, []);

  return (
    <div className="mx-auto max-w-6xl space-y-8 px-4 py-8 sm:px-6">
      {/* Quick actions */}
      <section aria-labelledby="quick-actions-heading">
        <h2
          id="quick-actions-heading"
          className="mb-3 text-xs font-semibold uppercase tracking-widest text-zinc-400"
        >
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {QUICK_ACTIONS.map((a) => (
            <QuickActionCard key={a.label} {...a} />
          ))}
        </div>
      </section>

      {/* Stats */}
      <section aria-labelledby="stats-heading">
        <h2
          id="stats-heading"
          className="mb-3 text-xs font-semibold uppercase tracking-widest text-zinc-400"
        >
          Usage
        </h2>
        {loading ? (
          <StatsCardSkeleton cards={4} />
        ) : stats ? (
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <StatsCard value={stats.total_requests} label="Total Requests" />
            <StatsCard value={stats.total_plans} label="Plans Created" />
            <StatsCard value={stats.connected_tools} label="Connected Tools" />
            <StatsCard value={`${stats.success_rate}%`} label="Success Rate" />
          </div>
        ) : null}
      </section>

      {/* Activity + Connected services */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section
          aria-labelledby="activity-heading"
          className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
        >
          <div className="mb-3 flex items-center justify-between">
            <h2
              id="activity-heading"
              className="text-sm font-semibold text-zinc-900 dark:text-zinc-50"
            >
              Recent Activity
            </h2>
            <Link
              href="/activity"
              className="text-xs font-semibold text-zinc-500 hover:text-zinc-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:hover:text-zinc-50"
            >
              View All →
            </Link>
          </div>
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-10 animate-pulse rounded-xl bg-zinc-100 dark:bg-zinc-800"
                />
              ))}
            </div>
          ) : (
            <ActivityList items={activity} />
          )}
        </section>

        <section
          aria-labelledby="services-heading"
          className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
        >
          <div className="mb-3 flex items-center justify-between">
            <h2
              id="services-heading"
              className="text-sm font-semibold text-zinc-900 dark:text-zinc-50"
            >
              Connected Services
            </h2>
            <Link
              href="/integrations"
              className="text-xs font-semibold text-zinc-500 hover:text-zinc-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:hover:text-zinc-50"
            >
              Manage →
            </Link>
          </div>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {servers.map((srv) => (
              <ServiceStatusCard key={srv.name} server={srv} />
            ))}
          </div>
        </section>
      </div>

      {/* Recent Plans */}
      <section
        aria-labelledby="plans-heading"
        className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
      >
        <div className="mb-3 flex items-center justify-between">
          <h2
            id="plans-heading"
            className="text-sm font-semibold text-zinc-900 dark:text-zinc-50"
          >
            Recent Plans
          </h2>
          <Link
            href="/plans"
            className="text-xs font-semibold text-zinc-500 hover:text-zinc-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:hover:text-zinc-50"
          >
            View All Plans →
          </Link>
        </div>
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <PlanCardSkeleton key={i} className="h-14" />
            ))}
          </div>
        ) : (
          <RecentPlansList plans={plans} />
        )}
      </section>
    </div>
  );
}
