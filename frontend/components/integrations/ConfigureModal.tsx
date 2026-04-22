"use client";

import { useEffect, useId, useRef } from "react";
import type { IntegrationViewModel } from "@/lib/integrations/types";

type Props = {
  integration: IntegrationViewModel | null;
  open: boolean;
  onClose: () => void;
};

export function ConfigureModal({ integration, open, onClose }: Props) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  const descId = useId();

  useEffect(() => {
    const el = dialogRef.current;
    if (!el) return;

    if (open) {
      if (!el.open) el.showModal();
      return;
    }

    if (el.open) el.close();
  }, [open]);

  useEffect(() => {
    const el = dialogRef.current;
    if (!el) return;

    const onCancel = (e: Event) => {
      e.preventDefault();
      onClose();
    };

    el.addEventListener("cancel", onCancel);
    return () => el.removeEventListener("cancel", onCancel);
  }, [onClose]);

  return (
    <dialog
      ref={dialogRef}
      className="w-[min(92vw,520px)] rounded-2xl border border-zinc-200 bg-white p-0 text-zinc-900 shadow-2xl backdrop:bg-black/40 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
      aria-labelledby={titleId}
      aria-describedby={descId}
      onClose={onClose}
    >
      {integration ? (
        <div className="p-6 sm:p-7">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 id={titleId} className="text-lg font-semibold tracking-tight">
                Configure {integration.title}
              </h2>
              <p id={descId} className="mt-2 text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
                These controls are ready to wire to your backend. For now they help validate layout and
                accessibility for the integrations module.
              </p>
            </div>
            <button
              type="button"
              className="rounded-lg p-2 text-zinc-500 transition hover:bg-zinc-100 hover:text-zinc-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:hover:bg-zinc-900 dark:hover:text-zinc-50 dark:focus-visible:outline-zinc-600"
              onClick={onClose}
              aria-label="Close configuration"
            >
              <span aria-hidden>×</span>
            </button>
          </div>

          <div className="mt-6 space-y-4">
            <label className="block text-sm font-medium text-zinc-800 dark:text-zinc-200">
              Display name
              <input
                className="mt-2 w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 shadow-sm outline-none ring-zinc-900/10 placeholder:text-zinc-400 focus:border-zinc-400 focus:ring-4 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-50 dark:ring-white/10 dark:focus:border-zinc-500"
                defaultValue={integration.accountLabel ?? ""}
                placeholder="Workspace or account label"
                autoComplete="off"
              />
            </label>

            <label className="block text-sm font-medium text-zinc-800 dark:text-zinc-200">
              Notes
              <textarea
                className="mt-2 min-h-[96px] w-full resize-y rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 shadow-sm outline-none ring-zinc-900/10 placeholder:text-zinc-400 focus:border-zinc-400 focus:ring-4 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-50 dark:ring-white/10 dark:focus:border-zinc-500"
                placeholder="Optional context for your team (stored when API is connected)"
                defaultValue=""
              />
            </label>
          </div>

          <div className="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <button
              type="button"
              className="inline-flex w-full min-h-[44px] items-center justify-center rounded-lg border border-zinc-300 bg-white px-4 py-2.5 text-sm font-semibold text-zinc-900 shadow-sm transition hover:bg-zinc-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900 dark:focus-visible:outline-zinc-600 sm:w-auto"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="button"
              className="inline-flex w-full min-h-[44px] items-center justify-center rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-zinc-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-900 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200 dark:focus-visible:outline-zinc-200 sm:w-auto"
              onClick={onClose}
            >
              Save
            </button>
          </div>
        </div>
      ) : null}
    </dialog>
  );
}
