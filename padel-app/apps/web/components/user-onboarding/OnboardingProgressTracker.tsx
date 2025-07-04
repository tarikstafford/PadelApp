"use client";

import React from 'react';
import { Check, Clock, ArrowRight } from 'lucide-react';
import { useUserOnboarding } from './UserOnboardingProvider';
import { ONBOARDING_STEPS, OnboardingStep } from './types';
import { cn } from '@/lib/utils';

interface OnboardingProgressTrackerProps {
  showDetails?: boolean;
  className?: string;
}

export function OnboardingProgressTracker({ 
  showDetails = true, 
  className = '' 
}: OnboardingProgressTrackerProps) {
  const { 
    currentStep, 
    completedSteps, 
    getStepProgress, 
    canNavigateToStep, 
    goToStep 
  } = useUserOnboarding();

  const getStepStatus = (stepId: OnboardingStep) => {
    if (completedSteps.includes(stepId)) return 'completed';
    if (stepId === currentStep) return 'active';
    return 'pending';
  };

  const currentStepIndex = ONBOARDING_STEPS.findIndex(s => s.id === currentStep);

  return (
    <div className={cn("w-full", className)}>
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-sm font-medium text-muted-foreground">
            Setup Progress
          </h2>
          <span className="text-sm font-medium text-muted-foreground">
            {getStepProgress()}%
          </span>
        </div>
        <div className="w-full bg-muted rounded-full h-2">
          <div 
            className="bg-primary h-2 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${getStepProgress()}%` }}
          />
        </div>
      </div>

      {/* Step Indicators */}
      <div className="space-y-4">
        {ONBOARDING_STEPS.map((step, index) => {
          const status = getStepStatus(step.id);
          const canNavigate = canNavigateToStep(step.id);
          const isClickable = canNavigate && step.id !== currentStep;

          return (
            <div key={step.id} className="flex items-start gap-4">
              {/* Step Number/Icon */}
              <div className="flex-shrink-0 relative">
                <button
                  onClick={() => isClickable && goToStep(step.id)}
                  disabled={!isClickable}
                  className={cn(
                    "w-10 h-10 rounded-full border-2 flex items-center justify-center transition-all duration-200",
                    {
                      "bg-primary border-primary text-primary-foreground": status === 'completed',
                      "bg-primary/10 border-primary text-primary ring-2 ring-primary/20": status === 'active',
                      "bg-muted border-muted-foreground/30 text-muted-foreground": status === 'pending',
                      "hover:border-primary/50 cursor-pointer": isClickable,
                      "cursor-not-allowed": !isClickable
                    }
                  )}
                >
                  {status === 'completed' ? (
                    <Check className="h-5 w-5" />
                  ) : status === 'active' ? (
                    <div className="w-3 h-3 bg-current rounded-full animate-pulse" />
                  ) : (
                    <span className="text-sm font-medium">{index + 1}</span>
                  )}
                </button>

                {/* Connector Line */}
                {index < ONBOARDING_STEPS.length - 1 && (
                  <div
                    className={cn(
                      "absolute top-10 left-1/2 transform -translate-x-px w-0.5 h-8 transition-colors duration-300",
                      {
                        "bg-primary": completedSteps.includes(step.id),
                        "bg-muted-foreground/30": !completedSteps.includes(step.id)
                      }
                    )}
                  />
                )}
              </div>

              {/* Step Content */}
              <div className="flex-1 min-w-0 pb-8">
                <div className="flex items-center gap-2 mb-1">
                  <h3
                    className={cn(
                      "text-sm font-medium transition-colors",
                      {
                        "text-primary": status === 'active' || status === 'completed',
                        "text-muted-foreground": status === 'pending'
                      }
                    )}
                  >
                    {step.icon} {step.title}
                  </h3>
                  
                  {status === 'active' && (
                    <ArrowRight className="h-4 w-4 text-primary animate-pulse" />
                  )}
                  
                  {step.isOptional && status === 'pending' && (
                    <span className="text-xs bg-muted text-muted-foreground px-2 py-1 rounded">
                      Optional
                    </span>
                  )}
                </div>

                {showDetails && (
                  <>
                    <p className="text-sm text-muted-foreground mb-2">
                      {step.description}
                    </p>
                    
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        <span>{step.estimatedTime}</span>
                      </div>
                      
                      {status === 'completed' && (
                        <span className="text-green-600 dark:text-green-400">
                          ✓ Completed
                        </span>
                      )}
                      
                      {status === 'active' && (
                        <span className="text-primary">
                          → In Progress
                        </span>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Current Step Info */}
      <div className="mt-6 p-4 bg-primary/5 border border-primary/20 rounded-lg">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-primary font-medium">
            Current Step: {ONBOARDING_STEPS[currentStepIndex]?.title}
          </span>
        </div>
        <p className="text-sm text-muted-foreground">
          {ONBOARDING_STEPS[currentStepIndex]?.description}
        </p>
        <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
          <Clock className="h-3 w-3" />
          <span>Estimated time: {ONBOARDING_STEPS[currentStepIndex]?.estimatedTime}</span>
        </div>
      </div>
    </div>
  );
}