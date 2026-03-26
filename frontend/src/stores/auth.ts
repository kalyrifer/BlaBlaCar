import { create } from 'zustand';
import { authApi, setAccessToken } from '../services/api';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string, phone: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  setUser: (user) => set({ user, isAuthenticated: !!user, isLoading: false }),

  login: async (email, password) => {
    const response = await authApi.login({ email, password });
    // Token is now stored in localStorage by authApi.login
    set({ user: response.data.user, isAuthenticated: true, isLoading: false });
  },

  register: async (email, password, name, phone) => {
    const response = await authApi.register({ email, password, name, phone });
    // After registration, the API returns access_token
    if (response.data.access_token) {
      // Store token in localStorage
      localStorage.setItem('access_token', response.data.access_token);
    }
    set({ user: response.data.user, isAuthenticated: true, isLoading: false });
  },

  logout: async () => {
    try {
      await authApi.logout();
    } finally {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  checkAuth: async () => {
    try {
      const response = await authApi.me();
      set({ user: response.data, isAuthenticated: true, isLoading: false });
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));
