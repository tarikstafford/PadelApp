"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { useRouter } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ''; // Get base URL from env

// Define a type for the user object
interface User {
  id?: number; // Changed from string to number to match backend User model ID type
  email: string;
  full_name?: string;
  profile_picture_url?: string; // Added profile_picture_url
  // Add other user properties as needed
}

// Define the shape of the AuthContext
export interface AuthContextType {
    user: User | null;
    setUser: React.Dispatch<React.SetStateAction<User | null>>;
    accessToken: string | null;
    setAccessToken: (token: string | null) => void;
    refreshToken: string | null;
    setRefreshToken: (token: string | null) => void;
    login: (token: string, refresh: string) => void;
    logout: () => void;
    register: (name: string, email: string, password: string) => Promise<void>;
    isLoading: boolean;
    fetchUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [accessToken, setAccessTokenState] = useState<string | null>(null);
    const [refreshToken, setRefreshTokenState] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    // DEBUG: Log the value of the environment variable at runtime
    useEffect(() => {
        console.log("NEXT_PUBLIC_API_URL as seen by client:", process.env.NEXT_PUBLIC_API_URL);
    }, []);

    const setAccessToken = (token: string | null) => {
        setAccessTokenState(token);
        if (typeof window !== 'undefined') {
            if (token) {
                localStorage.setItem('accessToken', token);
            } else {
                localStorage.removeItem('accessToken');
            }
        }
    };

    const setRefreshToken = (token: string | null) => {
        setRefreshTokenState(token);
        if (typeof window !== 'undefined') {
            if (token) {
                localStorage.setItem('refreshToken', token);
            } else {
                localStorage.removeItem('refreshToken');
            }
        }
    };

    const fetchAndUpdateUser = useCallback(async () => {
        const token = accessToken || (typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null);
        if (token) {
            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
                    headers: { 'Authorization': `Bearer ${token}` },
                });
                if (response.ok) {
                    const userData = await response.json();
                    setUser(userData);
                } else {
                    setUser(null);
                    setAccessToken(null);
                    setRefreshToken(null);
                }
            } catch (error) {
                console.error("Failed to fetch user", error);
                setUser(null);
            }
        }
        setIsLoading(false);
    }, [accessToken]);

    useEffect(() => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            setAccessTokenState(token);
            setRefreshTokenState(localStorage.getItem('refreshToken'));
        }
        fetchAndUpdateUser();
    }, [fetchAndUpdateUser]);

    const login = (token: string, refresh: string) => {
        setAccessToken(token);
        setRefreshToken(refresh);
        fetchAndUpdateUser();
    };

    const logout = () => {
        setUser(null);
        setAccessToken(null);
        setRefreshToken(null);
    };

    const register = async (name: string, email: string, password: string) => {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ full_name: name, email, password }),
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Registration failed');
        }
        // Optionally log the user in directly after registration
    };

    const value = {
        user,
        setUser,
        accessToken,
        setAccessToken,
        refreshToken,
        setRefreshToken,
        isLoading,
        login,
        logout,
        register,
        fetchUser: fetchAndUpdateUser,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use the AuthContext
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}; 