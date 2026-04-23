import type { SVGProps } from "react";

function IconGitHub(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden {...props}>
      <path
        fill="currentColor"
        d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.578.688.48C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"
      />
    </svg>
  );
}

/** Bento-style grid; reads as blocks / workspace (Notion-adjacent). */
function IconNotionBlocks(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden {...props}>
      <rect x="4" y="4" width="6" height="6" rx="1.25" fill="currentColor" />
      <rect x="13" y="4" width="7" height="4" rx="1.25" fill="currentColor" />
      <rect x="4" y="12" width="7" height="8" rx="1.25" fill="currentColor" />
      <rect x="13" y="10" width="7" height="10" rx="1.25" fill="currentColor" />
    </svg>
  );
}

function IconGoogleCalendar(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden {...props}>
      <path
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
        d="M8 2v3m8-3v3M3.5 9.09h17M21 8v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z"
      />
      <path stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" d="M8 14h2m4 0h2m-8 4h8" />
    </svg>
  );
}

function IconGmail(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden {...props}>
      <path
        fill="#EA4335"
        d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4-8 5L4 8V6l8 5 8-5v2z"
      />
    </svg>
  );
}

function IconPlus(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden stroke="currentColor" strokeWidth="2" strokeLinecap="round" {...props}>
      <path d="M12 5v14M5 12h14" />
    </svg>
  );
}

const INTEGRATIONS = [
  {
    name: "GitHub",
    cardBg: "bg-zinc-50 dark:bg-zinc-900/80",
    labelClass: "text-zinc-900 dark:text-zinc-50",
    iconPlate: "bg-white dark:bg-zinc-800 ring-1 ring-zinc-200 dark:ring-zinc-700",
    iconClass: "h-6 w-6 text-zinc-900 dark:text-zinc-100",
    Icon: IconGitHub,
  },
  {
    name: "Notion",
    cardBg: "bg-zinc-50 dark:bg-zinc-900/80",
    labelClass: "text-zinc-900 dark:text-zinc-50",
    iconPlate: "bg-white dark:bg-zinc-800 ring-1 ring-zinc-200 dark:ring-zinc-700",
    iconClass: "h-6 w-6 text-zinc-800 dark:text-zinc-200",
    Icon: IconNotionBlocks,
  },
  {
    name: "Google Calendar",
    cardBg: "bg-blue-50/90 dark:bg-blue-950/50",
    labelClass: "text-blue-900 dark:text-blue-100",
    iconPlate: "bg-white dark:bg-zinc-900 ring-1 ring-blue-200/80 dark:ring-blue-800/80",
    iconClass: "h-6 w-6 text-blue-600 dark:text-blue-400",
    Icon: IconGoogleCalendar,
  },
  {
    name: "Gmail",
    cardBg: "bg-red-50/90 dark:bg-red-950/50",
    labelClass: "text-red-900 dark:text-red-100",
    iconPlate: "bg-white dark:bg-zinc-900 ring-1 ring-red-200/80 dark:ring-red-900/50",
    iconClass: "h-5 w-6",
    Icon: IconGmail,
  },
  {
    name: "More soon",
    cardBg: "bg-zinc-50 dark:bg-zinc-900/80",
    labelClass: "text-zinc-500 dark:text-zinc-400",
    iconPlate: "bg-white dark:bg-zinc-800 ring-1 ring-zinc-200 dark:ring-zinc-700",
    iconClass: "h-6 w-6 text-zinc-400 dark:text-zinc-500",
    Icon: IconPlus,
  },
] as const;

export function IntegrationLogoGrid() {
  return (
    <section className="mx-auto max-w-4xl px-4 py-16 sm:px-6">
      <p className="mb-8 text-center text-sm font-semibold uppercase tracking-widest text-zinc-400">
        Works with your tools
      </p>
      <div className="flex flex-wrap items-center justify-center gap-4">
        {INTEGRATIONS.map(({ name, cardBg, labelClass, iconPlate, iconClass, Icon }) => (
          <div
            key={name}
            className={[
              "flex items-center gap-3 rounded-xl border border-zinc-200 px-4 py-3 dark:border-zinc-800",
              cardBg,
            ].join(" ")}
          >
            <span
              className={[
                "flex h-10 w-10 shrink-0 items-center justify-center rounded-lg",
                iconPlate,
              ].join(" ")}
              aria-hidden
            >
              <Icon className={iconClass} />
            </span>
            <span className={["text-sm font-semibold", labelClass].join(" ")}>{name}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
