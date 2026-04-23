"use client";

type Props = {
  onClick: () => void;
  disabled?: boolean;
};

export function ConfigureButton({ onClick, disabled }: Props) {
  return (
    <button
      type="button"
      className="inline-flex w-full min-h-[44px] min-w-0 items-center justify-center rounded-lg border border-zinc-300 bg-white px-4 py-2.5 text-sm font-semibold text-zinc-900 shadow-sm transition hover:bg-zinc-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 disabled:cursor-not-allowed disabled:opacity-60 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900 dark:focus-visible:outline-zinc-600 sm:w-auto sm:min-w-[132px]"
      disabled={disabled}
      onClick={onClick}
    >
      Configure
    </button>
  );
}
