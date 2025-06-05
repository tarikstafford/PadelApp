"use client"; // HOCs that use hooks need to be client components

import React, { ComponentType, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';

// Exporting the interface to resolve linter error
export interface WithAuthProps {}

export default function withAuth<P extends object>(
  WrappedComponent: ComponentType<P>
) {
  const ComponentWithAuth = (props: P & WithAuthProps) => {
    const { user, accessToken, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!isLoading && !accessToken) { // Check accessToken as user might be null briefly during init
        router.replace('/auth/login');
      }
    }, [user, accessToken, isLoading, router]);

    if (isLoading) {
      return <p>Loading...</p>; // Or a proper loading spinner component
    }

    if (!accessToken) { // Render nothing or a redirect message if not authenticated
      return null; // Or redirect immediately, though useEffect handles it
    }

    return <WrappedComponent {...props} />;
  };
  
  // Assign a display name for easier debugging in React DevTools
  const displayName = WrappedComponent.displayName || WrappedComponent.name || 'Component';
  ComponentWithAuth.displayName = `withAuth(${displayName})`;

  return ComponentWithAuth;
} 