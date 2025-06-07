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
    const response = await apiClient.post<{ access_token: string; role: string }>("/auth/login", data);
    setCookie("token", response.access_token);
    setCookie("role", response.role);
    const userData = await apiClient.get<User>("/auth/users/me");
    setUser(userData);
    setIsAuthenticated(true);
  };

  const register = async (data: any) => {
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

  const value = { user, isAuthenticated, isLoading, login, register, logout, hasRole };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}; 