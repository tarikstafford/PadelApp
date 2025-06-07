"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";

export function withRoleProtection(WrappedComponent: React.ComponentType, allowedRoles: string[]) {
  return function WithRoleProtection(props: any) {
    const { isAuthenticated, user, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!isLoading) {
        if (!isAuthenticated) {
          router.replace("/login");
        } else if (user && !allowedRoles.includes(user.role)) {
          router.replace("/unauthorized"); // Or a more appropriate page
        }
      }
    }, [isAuthenticated, user, isLoading, router]);

    if (isLoading || !isAuthenticated || !user || !allowedRoles.includes(user.role)) {
      return <div>Loading...</div>; // Or a spinner component
    }

    return <WrappedComponent {...props} />;
  };
} 