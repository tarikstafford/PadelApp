"use client";

import React from 'react';
import { Check, GamepadIcon, User, Trophy } from 'lucide-react';
import { useGameOnboarding } from './GameOnboardingProvider';
import { cn } from '@/lib/utils';

export function OnboardingProgressIndicator() {
  const { currentStep } = useGameOnboarding();

  const steps = [
    {
      id: 'preview',
      label: 'Game Preview',
      icon: GamepadIcon,
      description: 'View game details'
    },
    {
      id: 'auth',
      label: 'Authentication',
      icon: User,
      description: 'Sign in or create account'
    },
    {
      id: 'success',
      label: 'Joined!',
      icon: Trophy,
      description: 'Successfully joined game'
    }
  ];

  const getStepStatus = (stepId: string) => {
    const stepIndex = steps.findIndex(step => step.id === stepId);
    const currentIndex = steps.findIndex(step => step.id === currentStep);
    
    if (currentStep === 'joining' && stepId === 'success') {
      return 'loading';
    }
    
    if (stepIndex < currentIndex || currentStep === 'success') {
      return 'completed';
    } else if (stepIndex === currentIndex) {
      return 'active';
    } else {
      return 'pending';
    }
  };

  // Don't show progress indicator if there's an error or on initial preview
  if (currentStep === 'error' || currentStep === 'preview') {
    return null;
  }

  return (
    <div className="w-full max-w-md mx-auto mb-6">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const status = getStepStatus(step.id);
          const Icon = step.icon;
          
          return (
            <React.Fragment key={step.id}>
              <div className="flex flex-col items-center">
                {/* Step Circle */}
                <div
                  className={cn(
                    "w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-200",
                    {
                      "bg-primary border-primary text-primary-foreground": status === 'completed',
                      "bg-primary/10 border-primary text-primary animate-pulse": status === 'active',
                      "bg-muted border-muted-foreground/30 text-muted-foreground": status === 'pending',
                      "bg-primary/20 border-primary text-primary": status === 'loading'
                    }
                  )}
                >
                  {status === 'completed' ? (
                    <Check className="h-5 w-5" />
                  ) : status === 'loading' ? (
                    <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Icon className="h-5 w-5" />
                  )}
                </div>
                
                {/* Step Label */}
                <div className="text-center mt-2">
                  <p className={cn(
                    "text-xs font-medium transition-colors",
                    {
                      "text-primary": status === 'completed' || status === 'active' || status === 'loading',
                      "text-muted-foreground": status === 'pending'
                    }
                  )}>
                    {step.label}
                  </p>
                  <p className="text-xs text-muted-foreground hidden sm:block">
                    {step.description}
                  </p>
                </div>
              </div>
              
              {/* Connector Line */}
              {index < steps.length - 1 && (
                <div className="flex-1 mx-2">
                  <div
                    className={cn(
                      "h-0.5 transition-all duration-300",
                      {
                        "bg-primary": getStepStatus(steps[index + 1]?.id || '') === 'completed',
                        "bg-muted-foreground/30": getStepStatus(steps[index + 1]?.id || '') !== 'completed'
                      }
                    )}
                  />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}