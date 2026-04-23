"use client";

import { useMemo, useState } from "react";
import { DEMO_API_TOKENS, DEMO_TOKEN_USAGE, type DemoApiToken } from "@/lib/settings/demo";
import { SettingsSectionCard } from "../SettingsSectionCard";
import { GenerateTokenModal } from "./GenerateTokenModal";

function formatDate(iso: string) {
  return new Intl.DateTimeFormat("en-US", { dateStyle: "medium" }).format(new Date(iso));
}

function formatDateTime(iso: string) {
  return new Intl.DateTimeFormat("en-US", { dateStyle: "medium", timeStyle: "short" }).format(new Date(iso));
}

function createTokenValue() {
  const bytes = new Uint8Array(24);
  crypto.getRandomValues(bytes);
  let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]!);
  const b64 = btoa(bin).replaceAll("+", "x").replaceAll("/", "y").slice(0, 32);
  return `pai_sk_${b64}`;
}

export function TokensSettingsView() {
  const [tokens, setTokens] = useState<DemoApiToken[]>(() => [...DEMO_API_TOKENS]);
  const [modalOpen, setModalOpen] = useState(false);
  const [freshToken, setFreshToken] = useState<string | null>(null);

  const rows = useMemo(() => tokens, [tokens]);

  function openGenerate() {
    const name = window.prompt("Name this token", "CLI Token");
    if (name === null) return;
    const trimmed = name.trim();
    if (!trimmed) return;

    const value = createTokenValue();
    const now = new Date().toISOString();
    const newRow: DemoApiToken = {
      id: crypto.randomUUID(),
      name: trimmed,
      createdIso: now,
      lastUsedIso: null,
    };
    setTokens((t) => [newRow, ...t]);
    setFreshToken(value);
    setModalOpen(true);
  }

  function closeModal() {
    setModalOpen(false);
    setFreshToken(null);
  }

  async function copyExisting(value: string) {
    try {
      await navigator.clipboard.writeText(value);
    } catch {
      // no-op: UI can be extended with toast later
    }
  }

  function revoke(id: string, name: string) {
    const ok = window.confirm(`Revoke token "${name}"? Applications using it will stop working.`);
    if (!ok) return;
    setTokens((t) => t.filter((x) => x.id !== id));
  }

  function deleteAccount() {
    const ok = window.confirm(
      "Delete your account and all associated data? This action is irreversible in production once wired to the API.",
    );
    if (!ok) return;
    window.alert("Account deletion is not wired yet — this is a UI placeholder.");
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">API Tokens</h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
          Manage programmatic access, review usage, and control account-level destructive actions.
        </p>
      </div>

      <SettingsSectionCard title="Usage statistics" description="High-level usage for the current billing period (demo values).">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div className="rounded-2xl border border-zinc-200 bg-zinc-50 p-5 dark:border-zinc-800 dark:bg-zinc-900/30">
            <p className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
              {DEMO_TOKEN_USAGE.requestsThisMonth}
            </p>
            <p className="mt-1 text-sm font-medium text-zinc-700 dark:text-zinc-200">Requests this month</p>
          </div>
          <div className="rounded-2xl border border-zinc-200 bg-zinc-50 p-5 dark:border-zinc-800 dark:bg-zinc-900/30">
            <p className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
              {DEMO_TOKEN_USAGE.requestsThisWeek}
            </p>
            <p className="mt-1 text-sm font-medium text-zinc-700 dark:text-zinc-200">This week</p>
          </div>
          <div className="rounded-2xl border border-zinc-200 bg-zinc-50 p-5 dark:border-zinc-800 dark:bg-zinc-900/30">
            <p className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
              {DEMO_TOKEN_USAGE.successRatePct}%
            </p>
            <p className="mt-1 text-sm font-medium text-zinc-700 dark:text-zinc-200">Success rate</p>
          </div>
        </div>
      </SettingsSectionCard>

      <SettingsSectionCard title="API tokens" description="Tokens authenticate scripts, CI jobs, and editor extensions.">
        <div className="hidden overflow-hidden rounded-2xl border border-zinc-200 dark:border-zinc-800 md:block">
          <table className="w-full border-collapse text-left text-sm">
            <caption className="sr-only">API tokens</caption>
            <thead className="bg-zinc-50 text-xs font-semibold uppercase tracking-wide text-zinc-600 dark:bg-zinc-900/40 dark:text-zinc-300">
              <tr>
                <th scope="col" className="px-4 py-3">
                  Token name
                </th>
                <th scope="col" className="px-4 py-3">
                  Created
                </th>
                <th scope="col" className="px-4 py-3">
                  Last used
                </th>
                <th scope="col" className="px-4 py-3 text-right">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200 bg-white dark:divide-zinc-800 dark:bg-zinc-950">
              {rows.map((t) => (
                <tr key={t.id}>
                  <td className="px-4 py-4 font-medium text-zinc-900 dark:text-zinc-50">{t.name}</td>
                  <td className="px-4 py-4 text-zinc-600 dark:text-zinc-300">
                    <time dateTime={t.createdIso}>{formatDate(t.createdIso)}</time>
                  </td>
                  <td className="px-4 py-4 text-zinc-600 dark:text-zinc-300">
                    {t.lastUsedIso ? <time dateTime={t.lastUsedIso}>{formatDateTime(t.lastUsedIso)}</time> : "Never"}
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex justify-end gap-2">
                      <button
                        type="button"
                        className="rounded-lg px-3 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-400 dark:text-red-300 dark:hover:bg-red-950/30 dark:focus-visible:outline-red-700"
                        onClick={() => revoke(t.id, t.name)}
                      >
                        Revoke
                      </button>
                      <button
                        type="button"
                        className="rounded-lg px-3 py-2 text-sm font-semibold text-zinc-900 transition hover:bg-zinc-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:text-zinc-50 dark:hover:bg-zinc-900 dark:focus-visible:outline-zinc-600"
                        onClick={() => void copyExisting(`pai_sk_${t.id}_redacted`)}
                      >
                        Copy
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="space-y-3 md:hidden">
          {rows.map((t) => (
            <div
              key={t.id}
              className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-semibold text-zinc-900 dark:text-zinc-50">{t.name}</p>
                  <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
                    Created <time dateTime={t.createdIso}>{formatDate(t.createdIso)}</time>
                  </p>
                  <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
                    Last used{" "}
                    {t.lastUsedIso ? <time dateTime={t.lastUsedIso}>{formatDateTime(t.lastUsedIso)}</time> : "Never"}
                  </p>
                </div>
              </div>
              <div className="mt-4 flex flex-col gap-2 sm:flex-row">
                <button
                  type="button"
                  className="inline-flex w-full min-h-[44px] items-center justify-center rounded-lg border border-zinc-300 bg-white px-3 text-sm font-semibold text-zinc-900 shadow-sm transition hover:bg-zinc-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900 dark:focus-visible:outline-zinc-600 sm:w-auto"
                  onClick={() => void copyExisting(`pai_sk_${t.id}_redacted`)}
                >
                  Copy
                </button>
                <button
                  type="button"
                  className="inline-flex w-full min-h-[44px] items-center justify-center rounded-lg border border-red-200 bg-red-50 px-3 text-sm font-semibold text-red-900 transition hover:bg-red-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-400 dark:border-red-900/50 dark:bg-red-950/30 dark:text-red-100 dark:hover:bg-red-950/50 dark:focus-visible:outline-red-700 sm:w-auto"
                  onClick={() => revoke(t.id, t.name)}
                >
                  Revoke
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6">
          <button
            type="button"
            className="inline-flex w-full min-h-[44px] items-center justify-center rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-zinc-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-900 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200 dark:focus-visible:outline-zinc-200 sm:w-auto"
            onClick={openGenerate}
          >
            Generate New Token
          </button>
        </div>
      </SettingsSectionCard>

      <SettingsSectionCard
        title="Danger zone"
        description="Destructive actions that affect your entire account."
      >
        <div className="rounded-2xl border border-red-200 bg-red-50 p-5 dark:border-red-900/50 dark:bg-red-950/20">
          <p className="text-sm font-semibold text-red-950 dark:text-red-100">Delete all data</p>
          <p className="mt-2 text-sm leading-relaxed text-red-900/90 dark:text-red-100/90">
            Permanently delete your account and all associated data.
          </p>
          <button
            type="button"
            className="mt-4 inline-flex w-full min-h-[44px] items-center justify-center rounded-lg bg-red-700 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-red-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-700 dark:bg-red-600 dark:hover:bg-red-500 dark:focus-visible:outline-red-400 sm:w-auto"
            onClick={deleteAccount}
          >
            Delete Account
          </button>
        </div>
      </SettingsSectionCard>

      <GenerateTokenModal open={modalOpen} tokenValue={freshToken} onClose={closeModal} />
    </div>
  );
}
