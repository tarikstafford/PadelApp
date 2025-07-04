"use client";

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { OnboardingGuard } from '@/components/auth/OnboardingGuard';
import { UserOnboardingProvider } from '@/components/user-onboarding/UserOnboardingProvider';
import { UserOnboardingFlow } from '@/components/user-onboarding/UserOnboardingFlow';

export default function OnboardingPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Redirect to sign in if not authenticated
    if (!isLoading && !user) {
      router.push('/auth/signin?redirect=/onboarding');
      return;
    }
  }, [user, isLoading, router]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render anything if user is not authenticated (will redirect)
  if (!user) {
    return null;
  }

  return (
    <OnboardingGuard requireCompleted={false}>
      <UserOnboardingProvider>
        <UserOnboardingFlow />
      </UserOnboardingProvider>
    </OnboardingGuard>
  );
}