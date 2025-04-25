import { AuthenticationState } from "@/types/types";
import { create } from "zustand";

export const useAuthenticationStore = create(
  (set): AuthenticationState => ({
    isAuthenticated: false,
    login: () => set({ isAuthenticated: true }),
    logout: () => set({ isAuthenticated: false }),
  })
);

export const getIsAuthenticated = () => {
  return useAuthenticationStore.getState().isAuthenticated;
};
