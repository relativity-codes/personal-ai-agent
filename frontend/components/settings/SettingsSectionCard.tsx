type Props = {
  title: string;
  description?: string;
  children: React.ReactNode;
};

export function SettingsSectionCard({ title, description, children }: Props) {
  return (
    <section className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-950 sm:p-7">
      <header className="border-b border-zinc-100 pb-4 dark:border-zinc-800">
        <h2 className="text-base font-semibold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-lg">{title}</h2>
        {description ? (
          <p className="mt-2 text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">{description}</p>
        ) : null}
      </header>
      <div className="pt-6">{children}</div>
    </section>
  );
}
