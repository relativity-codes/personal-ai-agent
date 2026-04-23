export type SettingsNavItem = {
  href: string;
  label: string;
  description: string;
};

export const SETTINGS_NAV_ITEMS: readonly SettingsNavItem[] = [
  {
    href: "/settings/profile",
    label: "Profile",
    description: "Avatar and personal information",
  },
  {
    href: "/settings/preferences",
    label: "Preferences",
    description: "Defaults, working hours, and AI behavior",
  },
  {
    href: "/settings/tokens",
    label: "API Tokens",
    description: "Tokens, usage, and account deletion",
  },
] as const;
