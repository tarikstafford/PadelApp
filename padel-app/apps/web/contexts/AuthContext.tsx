"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ''; // Get base URL from env

// Define a type for the user object
interface User {
  id?: number; // Changed from string to number to match backend User model ID type
  email: string;
  name?: string;
  profile_picture_url?: string; // Added profile_picture_url
  // Add other user properties as needed
}

// Define the shape of the AuthContext
interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  isLoading: boolean;
  login: (email_or_token: string, password?: string) => Promise<void>; // Can accept email/pass or a token for session init
  logout: () => void;
  register: (name: string, email: string, password: string) => Promise<void>;
  fetchAndUpdateUser: () => Promise<void>; // Added for refreshing user data
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true); // Start with loading true to check session
  const router = useRouter();

  const fetchAndUpdateUser = async (token?: string) => {
    const currentToken = token || accessToken;
    if (!currentToken) {
      setUser(null); // Clear user if no token
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/users/me`, {
        headers: { 'Authorization': `Bearer ${currentToken}` },
      });
      if (response.ok) {
        const userData: User = await response.json();
        setUser(userData);
      } else {
        console.warn('Failed to fetch user data with token.');
        setUser(null); // Clear user on fetch failure
        // Optionally, try to refresh token here if status is 401 and refresh token exists
        // For now, we'll just clear the user state.
        if (response.status === 401) {
            // Attempt to logout to clear tokens if user fetch fails due to auth
            logout(); // This will redirect to login
        }
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
      setUser(null);
    }
  };

  // Effect to check for existing session on initial load
  useEffect(() => {
    const attemptLoadSession = async () => {
      const storedAccessToken = localStorage.getItem('access_token');
      const storedRefreshToken = localStorage.getItem('refresh_token');

      if (storedAccessToken) {
        setAccessToken(storedAccessToken);
        setRefreshToken(storedRefreshToken);
        await fetchAndUpdateUser(storedAccessToken);
      }
      setIsLoading(false);
    };
    attemptLoadSession();
  }, []);

  const login = async (email_param: string, password_param?: string) => {
    setIsLoading(true);
    try {
      // For simplicity, this login function assumes email/password.
      // A more robust version might handle direct token setting for session recovery.
      if (!password_param) throw new Error("Password is required for login.");

      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username: email_param, password: password_param }).toString(),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Login failed");
      }
      setAccessToken(data.access_token);
      localStorage.setItem('access_token', data.access_token);
      if (data.refresh_token) {
        setRefreshToken(data.refresh_token);
        localStorage.setItem('refresh_token', data.refresh_token);
      }
      await fetchAndUpdateUser(data.access_token);
      router.push('/profile'); // Redirect to profile page
    } catch (error: any) {
      console.error("Login error in AuthContext:", error);
      // Clear any partial auth state
      logout(); // Use logout to ensure clean state
      throw error; // Re-throw for the form to catch and display
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name_param: string, email_param: string, password_param: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name_param, email: email_param, password: password_param }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Registration failed");
      }
      // Typically, after registration, you might redirect to login or show a success message.
      // Some apps might auto-login, but that requires another API call or token return from register.
      alert("Registration successful! Please log in.");
      router.push('/auth/login');
    } catch (error: any) {
      console.error("Registration error in AuthContext:", error);
      throw error; // Re-throw for the form to catch and display
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    router.push('/auth/login'); // Redirect to login page
  };

  return (
    <AuthContext.Provider value={{ user, accessToken, isLoading, login, logout, register, fetchAndUpdateUser }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the AuthContext
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 