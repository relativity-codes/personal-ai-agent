type Props = {
  icon: string;
  title: string;
  description: string;
};

export function FeatureCard({ icon, title, description }: Props) {
  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm transition hover:shadow-md dark:border-zinc-800 dark:bg-zinc-950">
      <div
        className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-zinc-100 text-xl dark:bg-zinc-900"
        aria-hidden
      >
        {icon}
      </div>
      <h3 className="mb-2 text-sm font-semibold text-zinc-900 dark:text-zinc-50">{title}</h3>
      <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">{description}</p>
    </div>
  );
}
