"use client";

import React from 'react';
import { useGameOnboarding } from './GameOnboardingProvider';
import { GamePreviewSidebar } from './GamePreviewSidebar';
import { AuthenticationModal } from './AuthenticationModal';
import { OnboardingProgressIndicator } from './OnboardingProgressIndicator';
import { JoinSuccessAnimation } from './JoinSuccessAnimation';
import { Card, CardContent } from '@workspace/ui/components/card';
import { Button } from '@workspace/ui/components/button';
import { AlertTriangle, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

export function GameOnboardingFlow() {
  const { currentStep, error, gameData, isLoading } = useGameOnboarding();
  const router = useRouter();

  const handleGoBack = () => {
    router.push('/games/public');
  };

  // Loading state
  if (isLoading && !gameData) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center space-y-4">
                <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
                <p className="text-muted-foreground">Loading game information...</p>
              </div>
            </div>
            <div className="hidden lg:block">
              <Card>
                <CardContent className="p-6">
                  <div className="animate-pulse space-y-4">
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                    <div className="h-8 bg-gray-200 rounded"></div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (currentStep === 'error') {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-md mx-auto">
          <Card>
            <CardContent className="p-6 text-center space-y-4">
              <AlertTriangle className="h-12 w-12 text-destructive mx-auto" />
              <h2 className="text-xl font-semibold">Unable to Load Game</h2>
              <p className="text-muted-foreground">
                {error || 'Something went wrong while loading the game invitation.'}
              </p>
              <div className="flex gap-2 justify-center">
                <Button onClick={handleGoBack} variant="outline">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Browse Games
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Success state
  if (currentStep === 'success') {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <OnboardingProgressIndicator />
          <JoinSuccessAnimation />
        </div>
      </div>
    );
  }

  // Main onboarding flow
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Progress Indicator */}
        <OnboardingProgressIndicator />

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-[1fr_350px]">
          {/* Main Content Area */}
          <div className="space-y-6">
            {/* Welcome Message */}
            {currentStep === 'preview' && gameData && (
              <Card>
                <CardContent className="p-6">
                  <div className="text-center space-y-4">
                    <h1 className="text-2xl font-bold">
                      You&apos;re Invited to Join a Padel Game!
                    </h1>
                    <p className="text-muted-foreground max-w-md mx-auto">
                      {gameData.creator.full_name || gameData.creator.email} has invited you to join their game at {gameData.game.booking.court.club?.name}.
                    </p>
                    {currentStep === 'preview' && (
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          Review the game details on the right and click &quot;Join Game&quot; to get started.
                        </p>
                        {!gameData.can_join && (
                          <p className="text-sm text-destructive">
                            {gameData.is_full ? 'This game is full.' : 
                             gameData.is_expired ? 'This invitation has expired.' : 
                             'Unable to join this game.'}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Joining State */}
            {currentStep === 'joining' && (
              <Card>
                <CardContent className="p-6">
                  <div className="text-center space-y-4">
                    <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
                    <h2 className="text-xl font-semibold">Joining Game...</h2>
                    <p className="text-muted-foreground">
                      Please wait while we add you to the game.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Mobile Game Preview (shown below on small screens) */}
            <div className="lg:hidden">
              <GamePreviewSidebar />
            </div>
          </div>

          {/* Sidebar - Game Preview (hidden on mobile) */}
          <div className="hidden lg:block">
            <GamePreviewSidebar className="sticky top-4" />
          </div>
        </div>

        {/* Authentication Modal */}
        <AuthenticationModal />
      </div>
    </div>
  );
}