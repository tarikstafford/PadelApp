"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { setCookie, getCookie, deleteCookie } from "cookies-next";
import { apiClient } from "@/lib/api";
import { User } from "@/lib/types"; // Assuming a User type is defined in types.ts

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  isLoading: boolean;
  login: (data: any) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  hasRole: (role: string) => boolean;
  updatePreferredPosition: (position: 'LEFT' | 'RIGHT') => Promise<void>;
  requestEloAdjustment: (requestedRating: number, reason: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const checkUser = async () => {
      const token = getCookie("token");
      if (token) {
        try {
          const userData = await apiClient.get<User>("/auth/users/me");
          setUser(userData);
          setIsAuthenticated(true);
        } catch (error) {
          console.error("Failed to fetch user", error);
          deleteCookie("token");
        }
      }
      setIsLoading(false);
    };
    checkUser();
  }, []);

  const login = async (data: any) => {
    const response = await apiClient.post<{ access_token: string; role: string }>(
      "/auth/login",
      { email: data.email, password: data.password }
    );
    setCookie("token", response.access_token);
    setCookie("role", response.role);
    const userData = await apiClient.get<User>("/auth/users/me");
    setUser(userData);
    setIsAuthenticated(true);
  };

  const register = async (data: any) => {
    console.log("Registering with data:", data);
    const response = await apiClient.post<{ access_token: string; role: string }>("/auth/register-club", data);
    setCookie("token", response.access_token);
    setCookie("role", response.role);
    const userData = await apiClient.get<User>("/auth/users/me");
    setUser(userData);
    setIsAuthenticated(true);
  };

  const logout = () => {
    deleteCookie("token");
    deleteCookie("role");
    setUser(null);
    setIsAuthenticated(false);
  };

  const hasRole = (role: string) => {
    return user?.role === role;
  };

  const updatePreferredPosition = async (position: 'LEFT' | 'RIGHT') => {
    if (!user) return;
    try {
      const response = await apiClient.put<User>(`/users/me`, { preferred_position: position });
      setUser(response);
    } catch (error) {
      console.error('Failed to update preferred position', error);
      throw error;
    }
  };

  const requestEloAdjustment = async (requestedRating: number, reason: string) => {
    if (!user) return;
    try {
      await apiClient.post(`/users/${user.id}/request-elo-adjustment`, {
        requested_rating: requestedRating,
        reason,
      });
    } catch (error) {
      console.error('Failed to request ELO adjustment', error);
      throw error;
    }
  };

  const value = { user, isAuthenticated, isLoading, login, register, logout, hasRole, updatePreferredPosition, requestEloAdjustment };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}; 