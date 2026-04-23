"use client";

import { useMemo, useRef, useState } from "react";
import { DEMO_PROFILE } from "@/lib/settings/demo";
import { inputClass, labelClass, readOnlyBoxClass } from "../form-classes";
import { SettingsSectionCard } from "../SettingsSectionCard";

export function ProfileSettingsView() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [name, setName] = useState(DEMO_PROFILE.name);
  const [savedAt, setSavedAt] = useState<string | null>(null);

  const memberSinceLabel = useMemo(
    () =>
      new Intl.DateTimeFormat("en-US", { month: "long", day: "numeric", year: "numeric" }).format(
        new Date(DEMO_PROFILE.memberSinceIso),
      ),
    [],
  );

  function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSavedAt(new Date().toISOString());
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">Profile</h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
          Manage your avatar and personal information. Changes here are ready to connect to your profile API.
        </p>
      </div>

      <SettingsSectionCard title="Avatar" description="Update the image shown across the product.">
        <div className="flex flex-col items-start gap-5 sm:flex-row sm:items-center">
          <div
            className="flex h-24 w-24 shrink-0 items-center justify-center rounded-2xl border border-zinc-200 bg-gradient-to-br from-zinc-100 to-zinc-200 text-2xl font-semibold text-zinc-800 shadow-inner dark:border-zinc-800 dark:from-zinc-900 dark:to-zinc-950 dark:text-zinc-100"
            aria-hidden
          >
            {name
              .split(" ")
              .map((p) => p[0])
              .join("")
              .slice(0, 2)
              .toUpperCase()}
          </div>
          <div className="w-full min-w-0 sm:w-auto">
            <input ref={fileInputRef} type="file" accept="image/*" className="sr-only" />
            <button
              type="button"
              className="inline-flex w-full min-h-[44px] items-center justify-center rounded-lg border border-zinc-300 bg-white px-4 py-2.5 text-sm font-semibold text-zinc-900 shadow-sm transition hover:bg-zinc-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900 dark:focus-visible:outline-zinc-600 sm:w-auto"
              onClick={() => fileInputRef.current?.click()}
            >
              Change Avatar
            </button>
            <p className="mt-2 text-xs text-zinc-500 dark:text-zinc-400">PNG or JPG, up to 5MB (upload wiring pending).</p>
          </div>
        </div>
      </SettingsSectionCard>

      <form onSubmit={handleSave}>
        <SettingsSectionCard title="Personal info" description="Your account details and identifiers.">
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
              />
            </div>

            <div>
              <span className={labelClass}>Email</span>
              <div className={readOnlyBoxClass}>
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <span className="break-all">{DEMO_PROFILE.email}</span>
                  <span className="inline-flex w-fit items-center rounded-full bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-900 ring-1 ring-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-100 dark:ring-emerald-900/60">
                    Verified
                  </span>
                </div>
              </div>
            </div>

            <div>
              <span className={labelClass}>User ID</span>
              <div className={readOnlyBoxClass}>
                <code className="text-sm">{DEMO_PROFILE.userId}</code>
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
              className="inline-flex w-full min-h-[44px] items-center justify-center rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-zinc-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-900 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200 dark:focus-visible:outline-zinc-200 sm:w-auto"
            >
              Save
            </button>
            {savedAt ? (
              <p className="text-sm text-emerald-700 dark:text-emerald-300" role="status">
                Saved locally — connect API to persist.
              </p>
            ) : null}
          </div>
        </SettingsSectionCard>
      </form>
    </div>
  );
}
