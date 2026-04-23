"use client";

import { useEffect, useId, useRef, useState } from "react";

type Props = {
  open: boolean;
  tokenValue: string | null;
  onClose: () => void;
};

export function GenerateTokenModal({ open, tokenValue, onClose }: Props) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  const descId = useId();
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const el = dialogRef.current;
    if (!el) return;
    if (open) {
      if (!el.open) el.showModal();
    } else if (el.open) {
      el.close();
    }
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

  useEffect(() => {
    if (!open) setCopied(false);
  }, [open]);

  async function copyToken() {
    if (!tokenValue) return;
    try {
      await navigator.clipboard.writeText(tokenValue);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  return (
    <dialog
      ref={dialogRef}
      className="w-[min(92vw,560px)] rounded-2xl border border-zinc-200 bg-white p-0 text-zinc-900 shadow-2xl backdrop:bg-black/40 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
      aria-labelledby={titleId}
      aria-describedby={descId}
      onClose={onClose}
    >
      <div className="p-6 sm:p-7">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 id={titleId} className="text-lg font-semibold tracking-tight">
              New API token
            </h2>
            <p id={descId} className="mt-2 text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
              Copy this token now. For security, it won&apos;t be shown again after you close this dialog.
            </p>
          </div>
          <button
            type="button"
            className="rounded-lg p-2 text-zinc-500 transition hover:bg-zinc-100 hover:text-zinc-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:hover:bg-zinc-900 dark:hover:text-zinc-50 dark:focus-visible:outline-zinc-600"
            onClick={onClose}
            aria-label="Close"
          >
            <span aria-hidden>×</span>
          </button>
        </div>

        {tokenValue ? (
          <div className="mt-6">
            <label className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400" htmlFor="new-token-value">
              Token
            </label>
            <div className="mt-2 flex flex-col gap-3 sm:flex-row sm:items-stretch">
              <input
                id="new-token-value"
                readOnly
                value={tokenValue}
                className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-3 font-mono text-xs text-zinc-900 shadow-inner dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50 sm:text-sm"
              />
              <button
                type="button"
                className="inline-flex w-full min-h-[44px] shrink-0 items-center justify-center rounded-xl bg-zinc-900 px-4 text-sm font-semibold text-white transition hover:bg-zinc-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-900 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200 dark:focus-visible:outline-zinc-200 sm:w-auto"
                onClick={() => void copyToken()}
              >
                {copied ? "Copied" : "Copy"}
              </button>
            </div>
          </div>
        ) : null}

        <div className="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            className="inline-flex w-full min-h-[44px] items-center justify-center rounded-lg border border-zinc-300 bg-white px-4 py-2.5 text-sm font-semibold text-zinc-900 shadow-sm transition hover:bg-zinc-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900 dark:focus-visible:outline-zinc-600 sm:w-auto"
            onClick={onClose}
          >
            Done
          </button>
        </div>
      </div>
    </dialog>
  );
}
