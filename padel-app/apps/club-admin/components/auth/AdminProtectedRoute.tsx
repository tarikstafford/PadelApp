"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { UserRole } from "@/lib/types"; // Assuming UserRole enum is here

const AdminProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    } else if (!isLoading && user && ![UserRole.ADMIN, UserRole.SUPER_ADMIN].includes(user.role)) {
      router.push("/login"); // Or a dedicated "unauthorized" page
    }
  }, [isLoading, isAuthenticated, user, router]);

  if (isLoading || !isAuthenticated) {
    // You can return a loading spinner or some placeholder here
    return <div>Loading...</div>;
  }

  return <>{children}</>;
};

export default AdminProtectedRoute; 