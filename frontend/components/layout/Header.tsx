"use client";

import { useAuth } from "@/lib/hooks/useAuth";
import { LogOut, User as UserIcon } from "lucide-react";
import { apiFetch } from "@/lib/api/client";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

export function Header() {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await apiFetch("/auth/logout", { method: "POST" });
      logout();
      toast.success("Logged out successfully");
      router.push("/");
    } catch (err) {
      toast.error("Logout failed");
    }
  };

  return (
    <header className="sticky top-0 z-50 flex items-center justify-between border-b border-zinc-200 bg-white/80 px-6 py-4 backdrop-blur-md">
      <div className="flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 font-bold text-white shadow-lg shadow-indigo-200">
          A
        </div>
        <h1 className="font-semibold tracking-tight text-zinc-900">
          Antigravity AI
        </h1>
      </div>

      <div className="flex items-center gap-4">
        {user ? (
          <div className="flex items-center gap-3">
            <div className="mr-2 flex flex-col items-end">
              <span className="text-sm font-medium text-zinc-900">
                {user.name || "User"}
              </span>
              <span className="text-xs font-normal text-zinc-500">
                {user.email}
              </span>
            </div>
            {user.avatar_url ? (
              <img
                src={user.avatar_url}
                alt={user.name || "User"}
                className="h-9 w-9 rounded-full border border-zinc-200 object-cover shadow-sm"
              />
            ) : (
              <div className="flex h-9 w-9 items-center justify-center rounded-full border border-zinc-200 bg-zinc-100 shadow-sm">
                <UserIcon className="h-5 w-5 text-zinc-400" />
              </div>
            )}
            <button
              onClick={handleLogout}
              className="ml-2 rounded-full p-2 text-zinc-400 transition-all duration-200 hover:bg-red-50 hover:text-red-600"
              title="Sign Out"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm italic text-zinc-400">
            Not signed in
          </div>
        )}
      </div>
    </header>
  );
}
