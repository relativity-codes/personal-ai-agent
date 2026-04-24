/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-unused-vars */
"use client";

import { useEffect, useState } from "react";
import { fetchAllChatHistory } from "@/lib/chat/api";
import { formatDistanceToNow } from "date-fns";
import { MessageSquare, User, Bot, ChevronRight } from "lucide-react";
import Link from "next/link";

type ChatActivity = {
  id: string;
  session_id: string;
  role: string;
  message: string;
  timestamp: string;
};

export function ActivityList() {
  const [activities, setActivities] = useState<ChatActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadActivities() {
      try {
        const result: any = await fetchAllChatHistory();
        if (result.success && result.data) {
          setActivities(result.data);
        } else {
          setError(result?.error || "Failed to load activities");
        }
      } catch (err) {
        setError("An unexpected error occurred");
      } finally {
        setLoading(false);
      }
    }

    loadActivities();
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="animate-pulse rounded-lg border border-zinc-200 p-4 dark:border-zinc-800"
          >
            <div className="mb-2 h-4 w-1/4 rounded bg-zinc-200 dark:bg-zinc-800"></div>
            <div className="h-3 w-3/4 rounded bg-zinc-100 dark:bg-zinc-900"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-600 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-400">
        {error}
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <div className="py-20 text-center">
        <MessageSquare className="mx-auto mb-4 h-12 w-12 text-zinc-300 dark:text-zinc-700" />
        <h3 className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
          No activity yet
        </h3>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
          Start a conversation with your AI agent to see your activity here.
        </p>
        <Link
          href="/chat"
          className="mt-6 inline-flex items-center rounded-full bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
        >
          Start Chatting
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {activities.map((activity) => (
        <div
          key={activity.id}
          className="group relative overflow-hidden rounded-xl border border-zinc-200 bg-white p-4 transition-all hover:border-zinc-300 hover:shadow-sm dark:border-zinc-800 dark:bg-zinc-950 dark:hover:border-zinc-700"
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3">
              <div
                className={`mt-1 rounded-full p-2 ${
                  activity.role === "user"
                    ? "bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400"
                    : "bg-purple-50 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400"
                }`}
              >
                {activity.role === "user" ? (
                  <User size={16} />
                ) : (
                  <Bot size={16} />
                )}
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                    {activity.role === "user" ? "You" : "AI Agent"}
                  </span>
                  <span className="text-xs text-zinc-300 dark:text-zinc-600">
                    •
                  </span>
                  <span className="text-xs text-zinc-400">
                    {formatDistanceToNow(new Date(activity.timestamp), {
                      addSuffix: true,
                    })}
                  </span>
                </div>
                <p className="mt-1.5 line-clamp-2 text-sm leading-relaxed text-zinc-700 dark:text-zinc-300">
                  {activity.message}
                </p>
                <div className="mt-3 flex items-center space-x-4">
                  <Link
                    href={`/chat?session_id=${activity.session_id}`}
                    className="inline-flex items-center text-xs font-medium text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                  >
                    View Session <ChevronRight size={12} className="ml-1" />
                  </Link>
                  <span className="font-mono text-[10px] text-zinc-300 dark:text-zinc-700">
                    ID: {activity.session_id.slice(0, 8)}...
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Subtle accent line based on role */}
          <div
            className={`absolute bottom-0 left-0 h-1 w-full opacity-0 transition-opacity group-hover:opacity-100 ${
              activity.role === "user" ? "bg-blue-500" : "bg-purple-500"
            }`}
          />
        </div>
      ))}
    </div>
  );
}
