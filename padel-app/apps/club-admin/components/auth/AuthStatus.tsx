"use client";

import { useAuth } from "@/contexts/AuthContext";

export default function AuthStatus() {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex items-center p-4 border-b">
      <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center font-bold text-lg mr-4">
        {user?.name?.charAt(0).toUpperCase() || "A"}
      </div>
      <div>
        <p className="font-semibold">{user?.name}</p>
        <p className="text-sm text-gray-500">{user?.email}</p>
      </div>
    </div>
  );
} 