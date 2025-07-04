"use client";

import React from 'react';
import { useUserOnboarding } from './UserOnboardingProvider';
import { OnboardingProgressTracker } from './OnboardingProgressTracker';
import { WelcomeStep } from './steps/WelcomeStep';
import { PositionSelectionStep } from './steps/PositionSelectionStep';
import { ExperienceAssessmentStep } from './steps/ExperienceAssessmentStep';
import { EloEstimationStep } from './steps/EloEstimationStep';
import { FeatureIntroductionStep } from './steps/FeatureIntroductionStep';
import { CompleteStep } from './steps/CompleteStep';

export function UserOnboardingFlow() {
  const { currentStep, error } = useUserOnboarding();

  const renderStep = () => {
    switch (currentStep) {
      case 'welcome':
        return <WelcomeStep />;
      case 'position':
        return <PositionSelectionStep />;
      case 'experience':
        return <ExperienceAssessmentStep />;
      case 'elo-estimation':
        return <EloEstimationStep />;
      case 'features':
        return <FeatureIntroductionStep />;
      case 'complete':
        return <CompleteStep />;
      default:
        return <WelcomeStep />;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Progress Tracker */}
        <div className="mb-8">
          <OnboardingProgressTracker />
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 dark:bg-red-950 dark:border-red-800 dark:text-red-300">
            {error}
          </div>
        )}

        {/* Step Content */}
        <div className="w-full">
          {renderStep()}
        </div>
      </div>
    </div>
  );
}