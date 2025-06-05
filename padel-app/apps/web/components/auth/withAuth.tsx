"use client"; // HOCs that use hooks need to be client components

import React, { ComponentType, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';

// No props are passed by this HOC, so we can remove the empty interface
// export interface WithAuthProps {} // REMOVED

export default function withAuth<P extends object>(
  WrappedComponent: ComponentType<P>
) {
  const ComponentWithAuth = (props: P) => { // Removed WithAuthProps from here
    const { user, accessToken, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!isLoading && !accessToken) { // Check accessToken as user might be null briefly during init
        router.replace('/auth/login');
      }
    }, [user, accessToken, isLoading, router]);

    if (isLoading) {
      return <div className="flex justify-center items-center min-h-screen"><Loader2 className="h-12 w-12 animate-spin text-primary" /></div>; // Improved loading state
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