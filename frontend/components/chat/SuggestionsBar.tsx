const SUGGESTIONS = [
  "Prepare for tomorrow's standup",
  "Summarize my week",
  "What's on my calendar today?",
];

type Props = { onSelect: (text: string) => void };

export function SuggestionsBar({ onSelect }: Props) {
  return (
    <div className="flex flex-wrap gap-2" role="group" aria-label="Suggested prompts">
      {SUGGESTIONS.map((s) => (
        <button
          key={s}
          onClick={() => onSelect(s)}
          className="rounded-full border border-zinc-200 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 transition hover:border-zinc-300 hover:bg-zinc-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-300 dark:hover:border-zinc-700 dark:hover:bg-zinc-900"
        >
          {s}
        </button>
      ))}
    </div>
  );
}
