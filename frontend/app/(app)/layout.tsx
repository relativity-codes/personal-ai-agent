import { AppChrome } from "@/components/shared/shell/AppChrome";

export default function AppShellLayout({ children }: { children: React.ReactNode }) {
  return <AppChrome>{children}</AppChrome>;
}
