type Props = {
  value: number | string;
  label: string;
};

export function StatsCard({ value, label }: Props) {
  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
      <p className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">{value}</p>
      <p className="mt-1 text-xs text-zinc-500">{label}</p>
    </div>
  );
}
