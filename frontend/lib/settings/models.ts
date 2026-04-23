export const MODEL_OPTIONS: readonly { value: string; label: string }[] = [
  { value: "claude-3-5-sonnet", label: "Claude 3.5 Sonnet (Balanced)" },
  { value: "claude-3-5-haiku", label: "Claude 3.5 Haiku (Fast)" },
  { value: "gpt-4o", label: "GPT-4o" },
  { value: "gpt-4o-mini", label: "GPT-4o mini" },
] as const;
