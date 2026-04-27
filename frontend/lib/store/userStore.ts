import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  created_at?: string | number | Date;
  id: string;
  google_id: string;
  email: string;
  name?: string;
  avatar_url?: string;
  timezone?: string;
  default_MY_GITHUB_repo?: string;
  default_notion_db?: string;
  is_active?: boolean;
}

interface UserState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  setUser: (user: User | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      user: null,
      isLoading: false,
      error: null,
      setUser: (user) => set({ user, error: null }),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      logout: () => set({ user: null, error: null }),
    }),
    {
      name: 'user-storage',
    }
  )
);
