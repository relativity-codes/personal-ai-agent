import { useEffect } from 'react';
import { useUserStore } from '@/lib/store/userStore';
import { apiFetch } from '@/lib/api/client';

export function useAuth() {
  const { user, setUser, setLoading, setError, logout } = useUserStore();

  const fetchUser = async () => {
    setLoading(true);
    try {
      const response = await apiFetch<any>('/api/v1/users/me');
      if (response.success) {
        setUser(response.data);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch user');
      if (err.status === 401) {
        logout();
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!user) {
      fetchUser();
    }
  }, []);

  return { user, fetchUser, logout };
}
