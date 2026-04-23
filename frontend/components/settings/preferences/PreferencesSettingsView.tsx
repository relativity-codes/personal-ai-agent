"use client";

import { useMemo, useState } from "react";
import {
  DEMO_PREFERENCES,
  WORKDAY_KEYS,
  WORKDAY_LABELS,
  type DemoPreferences,
} from "@/lib/settings/demo";
import { MODEL_OPTIONS } from "@/lib/settings/models";
import { COMMON_TIMEZONES } from "@/lib/settings/timezones";
import { inputClass, labelClass } from "../form-classes";
import { SettingsSectionCard } from "../SettingsSectionCard";

function clonePrefs(p: DemoPreferences): DemoPreferences {
  return {
    ...p,
    workingDays: { ...p.workingDays },
  };
}

export function PreferencesSettingsView() {
  const baseline = useMemo(() => clonePrefs(DEMO_PREFERENCES), []);
  const [prefs, setPrefs] = useState<DemoPreferences>(() => clonePrefs(DEMO_PREFERENCES));
  const [savedAt, setSavedAt] = useState<string | null>(null);

  function setWorkingDay(day: (typeof WORKDAY_KEYS)[number], checked: boolean) {
    setPrefs((p) => ({ ...p, workingDays: { ...p.workingDays, [day]: checked } }));
  }

  function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSavedAt(new Date().toISOString());
  }

  function handleReset() {
    setPrefs(clonePrefs(baseline));
    setSavedAt(null);
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">Preferences</h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
          Defaults for repositories, working hours, notifications, and AI behavior.
        </p>
      </div>

      <form className="space-y-6" onSubmit={handleSave}>
        <SettingsSectionCard title="Default repository" description="Used when a command needs a repo context.">
          <label className={labelClass} htmlFor="default-github-repo">
            Default GitHub repo
          </label>
          <input
            id="default-github-repo"
            className={inputClass}
            value={prefs.defaultGithubRepo}
            onChange={(e) => setPrefs((p) => ({ ...p, defaultGithubRepo: e.target.value }))}
            placeholder="org/repo"
            autoComplete="off"
          />

          <div className="mt-5">
            <label className={labelClass} htmlFor="default-notion-db">
              Default Notion database
            </label>
            <input
              id="default-notion-db"
              className={inputClass}
              value={prefs.defaultNotionDb}
              onChange={(e) => setPrefs((p) => ({ ...p, defaultNotionDb: e.target.value }))}
              autoComplete="off"
            />
          </div>
        </SettingsSectionCard>

        <SettingsSectionCard title="Working hours" description="Helps the agent schedule and summarize around your day.">
          <label className={labelClass} htmlFor="timezone">
            Timezone
          </label>
          <select
            id="timezone"
            className={inputClass}
            value={prefs.timezone}
            onChange={(e) => setPrefs((p) => ({ ...p, timezone: e.target.value }))}
          >
            {COMMON_TIMEZONES.map((tz) => (
              <option key={tz} value={tz}>
                {tz}
              </option>
            ))}
          </select>

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <div>
              <label className={labelClass} htmlFor="work-start">
                Working hours start
              </label>
              <input
                id="work-start"
                type="time"
                className={inputClass}
                value={prefs.workingStart}
                onChange={(e) => setPrefs((p) => ({ ...p, workingStart: e.target.value }))}
              />
            </div>
            <div>
              <label className={labelClass} htmlFor="work-end">
                Working hours end
              </label>
              <input
                id="work-end"
                type="time"
                className={inputClass}
                value={prefs.workingEnd}
                onChange={(e) => setPrefs((p) => ({ ...p, workingEnd: e.target.value }))}
              />
            </div>
          </div>

          <fieldset className="mt-6">
            <legend className={labelClass}>Working days</legend>
            <div className="mt-3 flex flex-wrap gap-2">
              {WORKDAY_KEYS.map((day) => {
                const id = `workday-${day}`;
                return (
                  <label
                    key={day}
                    htmlFor={id}
                    className="inline-flex min-h-[44px] min-w-[52px] cursor-pointer select-none items-center justify-center rounded-xl border border-zinc-200 bg-white px-3 text-sm font-semibold text-zinc-800 shadow-sm transition hover:bg-zinc-50 has-[:checked]:border-zinc-900 has-[:checked]:bg-zinc-900 has-[:checked]:text-white dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-100 dark:hover:bg-zinc-900 dark:has-[:checked]:border-zinc-50 dark:has-[:checked]:bg-zinc-50 dark:has-[:checked]:text-zinc-900"
                  >
                    <input
                      id={id}
                      type="checkbox"
                      className="sr-only"
                      checked={prefs.workingDays[day]}
                      onChange={(e) => setWorkingDay(day, e.target.checked)}
                    />
                    {WORKDAY_LABELS[day]}
                  </label>
                );
              })}
            </div>
          </fieldset>
        </SettingsSectionCard>

        <SettingsSectionCard title="Notification preferences" description="Choose what we email you about.">
          <div className="space-y-4">
            <label className="flex cursor-pointer items-start gap-3 text-sm text-zinc-800 dark:text-zinc-100">
              <input
                type="checkbox"
                className="mt-1 h-4 w-4 rounded border-zinc-300 text-zinc-900 focus:ring-zinc-900 dark:border-zinc-600 dark:bg-zinc-950 dark:focus:ring-zinc-200"
                checked={prefs.emailWeeklySummaries}
                onChange={(e) => setPrefs((p) => ({ ...p, emailWeeklySummaries: e.target.checked }))}
              />
              <span>Email me weekly summaries</span>
            </label>
            <label className="flex cursor-pointer items-start gap-3 text-sm text-zinc-800 dark:text-zinc-100">
              <input
                type="checkbox"
                className="mt-1 h-4 w-4 rounded border-zinc-300 text-zinc-900 focus:ring-zinc-900 dark:border-zinc-600 dark:bg-zinc-950 dark:focus:ring-zinc-200"
                checked={prefs.notifyLongTasks}
                onChange={(e) => setPrefs((p) => ({ ...p, notifyLongTasks: e.target.checked }))}
              />
              <span>Notify when long-running tasks complete</span>
            </label>
            <label className="flex cursor-pointer items-start gap-3 text-sm text-zinc-800 dark:text-zinc-100">
              <input
                type="checkbox"
                className="mt-1 h-4 w-4 rounded border-zinc-300 text-zinc-900 focus:ring-zinc-900 dark:border-zinc-600 dark:bg-zinc-950 dark:focus:ring-zinc-200"
                checked={prefs.dailyDigest}
                onChange={(e) => setPrefs((p) => ({ ...p, dailyDigest: e.target.checked }))}
              />
              <span>Daily digest of activity</span>
            </label>
          </div>
        </SettingsSectionCard>

        <SettingsSectionCard title="AI preferences" description="Tune default model behavior for new sessions.">
          <label className={labelClass} htmlFor="default-model">
            Default model
          </label>
          <select
            id="default-model"
            className={inputClass}
            value={prefs.defaultModel}
            onChange={(e) => setPrefs((p) => ({ ...p, defaultModel: e.target.value }))}
          >
            {MODEL_OPTIONS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>

          <fieldset className="mt-6">
            <legend className={labelClass}>Response style</legend>
            <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-3">
              {(
                [
                  { id: "style-concise", value: "concise", label: "Concise" },
                  { id: "style-detailed", value: "detailed", label: "Detailed" },
                  { id: "style-auto", value: "auto", label: "Auto" },
                ] as const
              ).map((opt) => (
                <label
                  key={opt.value}
                  htmlFor={opt.id}
                  className="flex min-h-[44px] cursor-pointer items-center justify-center rounded-xl border border-zinc-200 bg-white px-3 text-sm font-semibold text-zinc-800 shadow-sm transition hover:bg-zinc-50 has-[:checked]:border-zinc-900 has-[:checked]:bg-zinc-900 has-[:checked]:text-white dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-100 dark:hover:bg-zinc-900 dark:has-[:checked]:border-zinc-50 dark:has-[:checked]:bg-zinc-50 dark:has-[:checked]:text-zinc-900"
                >
                  <input
                    id={opt.id}
                    type="radio"
                    name="response-style"
                    className="sr-only"
                    value={opt.value}
                    checked={prefs.responseStyle === opt.value}
                    onChange={() => setPrefs((p) => ({ ...p, responseStyle: opt.value }))}
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </fieldset>

          <div className="mt-6 space-y-4">
            <label className="flex cursor-pointer items-start gap-3 text-sm text-zinc-800 dark:text-zinc-100">
              <input
                type="checkbox"
                className="mt-1 h-4 w-4 rounded border-zinc-300 text-zinc-900 focus:ring-zinc-900 dark:border-zinc-600 dark:bg-zinc-950 dark:focus:ring-zinc-200"
                checked={prefs.streaming}
                onChange={(e) => setPrefs((p) => ({ ...p, streaming: e.target.checked }))}
              />
              <span>Enable streaming responses</span>
            </label>
            <label className="flex cursor-pointer items-start gap-3 text-sm text-zinc-800 dark:text-zinc-100">
              <input
                type="checkbox"
                className="mt-1 h-4 w-4 rounded border-zinc-300 text-zinc-900 focus:ring-zinc-900 dark:border-zinc-600 dark:bg-zinc-950 dark:focus:ring-zinc-200"
                checked={prefs.saveHistory}
                onChange={(e) => setPrefs((p) => ({ ...p, saveHistory: e.target.checked }))}
              />
              <span>Save conversation history</span>
            </label>
          </div>
        </SettingsSectionCard>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <button
            type="submit"
            className="inline-flex w-full min-h-[44px] items-center justify-center rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-zinc-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-900 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200 dark:focus-visible:outline-zinc-200 sm:w-auto"
          >
            Save
          </button>
          <button
            type="button"
            className="inline-flex w-full min-h-[44px] items-center justify-center rounded-lg border border-zinc-300 bg-white px-4 py-2.5 text-sm font-semibold text-zinc-900 shadow-sm transition hover:bg-zinc-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900 dark:focus-visible:outline-zinc-600 sm:w-auto"
            onClick={handleReset}
          >
            Reset
          </button>
          {savedAt ? (
            <p className="text-sm text-emerald-700 dark:text-emerald-300" role="status">
              Saved locally — connect API to persist.
            </p>
          ) : null}
        </div>
      </form>
    </div>
  );
}
