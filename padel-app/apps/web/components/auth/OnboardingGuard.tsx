"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { hasCompletedOnboarding } from '@/components/user-onboarding/utils/onboardingStorage';

interface OnboardingGuardProps {
  children: React.ReactNode;
  requireCompleted?: boolean;
}

/**
 * Component that checks if a user has completed onboarding and redirects appropriately.
 * 
 * @param requireCompleted - If true, redirects to onboarding if not completed
 * @param children - Children to render if onboarding check passes
 */
export function OnboardingGuard({ children, requireCompleted = false }: OnboardingGuardProps) {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [hasChecked, setHasChecked] = useState(false);

  useEffect(() => {
    if (isLoading || !user) return;

    const checkOnboarding = async () => {
      try {
        if (!user.id) {
          setHasChecked(true);
          return;
        }

        const completed = hasCompletedOnboarding(user.id);
        
        if (requireCompleted && !completed) {
          // User needs to complete onboarding
          router.push('/onboarding');
          return;
        }

        if (!requireCompleted && completed) {
          // User has completed onboarding, redirect to main app
          router.push('/profile');
          return;
        }

        setHasChecked(true);
      } catch (error) {
        console.error('Error checking onboarding status:', error);
        setHasChecked(true);
      }
    };

    checkOnboarding();
  }, [user, isLoading, router, requireCompleted]);

  // Show loading state while checking
  if (isLoading || !user || !hasChecked) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}