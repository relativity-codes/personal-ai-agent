"use client";

import { useMemo, useRef, useState, useEffect } from "react";
import { useAuth } from "@/lib/hooks/useAuth";
import { apiFetch } from "@/lib/api/client";
import { toast } from "sonner";
import { inputClass, labelClass, readOnlyBoxClass } from "../form-classes";
import { SettingsSectionCard } from "../SettingsSectionCard";

export function ProfileSettingsView() {
  const { user, fetchUser } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [name, setName] = useState("");
  const [timezone, setTimezone] = useState("UTC");
  const [githubRepo, setGithubRepo] = useState("");
  const [notionDb, setNotionDb] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (user) {
      setName(user.name || "");
      setTimezone(user.timezone || "UTC");
      setGithubRepo((user as any).default_github_repo || "");
      setNotionDb((user as any).default_notion_db || "");
    }
  }, [user]);

  const memberSinceLabel = useMemo(() => {
    if (!user?.created_at) return "N/A";
    return new Intl.DateTimeFormat("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    }).format(new Date(user.created_at));
  }, [user]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setIsSaving(true);
    try {
      await apiFetch("/api/v1/users/me", {
        method: "PATCH",
        body: JSON.stringify({
          name,
          timezone,
          default_github_repo: githubRepo,
          default_notion_db: notionDb,
        }),
      });
      await fetchUser();
      toast.success("Profile updated successfully");
    } catch (err: any) {
      toast.error(err.message || "Failed to update profile");
    } finally {
      setIsSaving(false);
    }
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const initials = name
    ? name.split(" ").map((p) => p[0]).join("").slice(0, 2).toUpperCase()
    : user.email?.[0].toUpperCase() || "?";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          Profile
        </h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
          Manage your avatar and personal information.
        </p>
      </div>

      <SettingsSectionCard
        title="Avatar"
        description="Update the image shown across the product."
      >
        <div className="flex flex-col items-start gap-5 sm:flex-row sm:items-center">
          {user.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={user.name || "User"}
              className="h-24 w-24 rounded-2xl border border-zinc-200 object-cover shadow-sm dark:border-zinc-800"
            />
          ) : (
            <div
              className="flex h-24 w-24 shrink-0 items-center justify-center rounded-2xl border border-zinc-200 bg-gradient-to-br from-indigo-500 to-purple-600 text-2xl font-bold text-white shadow-inner dark:border-zinc-800"
              aria-hidden
            >
              {initials}
            </div>
          )}
          <div className="w-full min-w-0 sm:w-auto">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="sr-only"
            />
            <button
              type="button"
              className="inline-flex w-full min-h-[44px] items-center justify-center rounded-lg border border-zinc-300 bg-white px-4 py-2.5 text-sm font-semibold text-zinc-900 shadow-sm transition hover:bg-zinc-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900 dark:focus-visible:outline-zinc-600 sm:w-auto"
              onClick={() => fileInputRef.current?.click()}
            >
              Change Avatar
            </button>
            <p className="mt-2 text-xs text-zinc-500 dark:text-zinc-400">
              PNG or JPG, up to 5MB (upload wiring pending).
            </p>
          </div>
        </div>
      </SettingsSectionCard>

      <form onSubmit={handleSave}>
        <SettingsSectionCard
          title="Personal info"
          description="Your account details and identifiers."
        >
          <div className="grid gap-5 lg:grid-cols-2">
            <div className="lg:col-span-2">
              <label className={labelClass} htmlFor="profile-name">
                Name
              </label>
              <input
                id="profile-name"
                name="name"
                className={inputClass}
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoComplete="name"
                placeholder="Enter your full name"
              />
            </div>

            <div className="lg:col-span-1">
              <label className={labelClass} htmlFor="profile-timezone">
                Timezone
              </label>
              <input
                id="profile-timezone"
                className={inputClass}
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                placeholder="e.g. UTC, America/New_York"
              />
            </div>

            <div className="lg:col-span-1">
              <label className={labelClass} htmlFor="profile-github">
                Default GitHub Repo
              </label>
              <input
                id="profile-github"
                className={inputClass}
                value={githubRepo}
                onChange={(e) => setGithubRepo(e.target.value)}
                placeholder="owner/repo"
              />
            </div>

            <div className="lg:col-span-1">
              <label className={labelClass} htmlFor="profile-notion">
                Default Notion DB
              </label>
              <input
                id="profile-notion"
                className={inputClass}
                value={notionDb}
                onChange={(e) => setNotionDb(e.target.value)}
                placeholder="Notion Database ID"
              />
            </div>

            <div>
              <span className={labelClass}>Email</span>
              <div className={readOnlyBoxClass}>
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <span className="break-all">{user.email}</span>
                  <span className="inline-flex w-fit items-center rounded-full bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-900 ring-1 ring-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-100 dark:ring-emerald-900/60">
                    Verified
                  </span>
                </div>
              </div>
            </div>

            <div>
              <span className={labelClass}>User ID</span>
              <div className={readOnlyBoxClass}>
                <code className="text-sm">{user.id}</code>
              </div>
            </div>

            <div className="lg:col-span-2">
              <span className={labelClass}>Member since</span>
              <div className={readOnlyBoxClass}>{memberSinceLabel}</div>
            </div>
          </div>

          <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:items-center">
            <button
              type="submit"
              disabled={isSaving}
              className="inline-flex w-full min-h-[44px] items-center justify-center rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-zinc-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-900 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200 dark:focus-visible:outline-zinc-200 sm:w-auto disabled:opacity-50"
            >
              {isSaving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </SettingsSectionCard>
      </form>
    </div>
  );
}
