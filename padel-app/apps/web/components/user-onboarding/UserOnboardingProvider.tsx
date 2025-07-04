"use client";

import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import { toast } from 'sonner';
import {
  UserOnboardingContextType,
  UserOnboardingState,
  OnboardingStep,
  OnboardingUserData,
  ExperienceAssessment,
  PreferredPosition,
  ONBOARDING_STEPS
} from './types';
import { calculateEstimatedElo } from './utils/eloEstimation';
import {
  saveOnboardingState,
  loadOnboardingState,
  clearOnboardingState,
  saveCurrentStep,
  markOnboardingCompleted,
  hasCompletedOnboarding
} from './utils/onboardingStorage';

const UserOnboardingContext = createContext<UserOnboardingContextType | undefined>(undefined);

type OnboardingAction =
  | { type: 'SET_CURRENT_STEP'; payload: OnboardingStep }
  | { type: 'ADD_COMPLETED_STEP'; payload: OnboardingStep }
  | { type: 'SET_CAN_PROCEED'; payload: boolean }
  | { type: 'UPDATE_USER_DATA'; payload: Partial<OnboardingUserData> }
  | { type: 'UPDATE_EXPERIENCE_DATA'; payload: Partial<ExperienceAssessment> }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ESTIMATED_ELO'; payload: number }
  | { type: 'LOAD_STATE'; payload: Partial<UserOnboardingState> }
  | { type: 'RESET_ONBOARDING' };

const initialUserData: OnboardingUserData = {
  experienceData: {},
  estimatedElo: 1.0,
  skipOptionalSteps: false
};

const initialState: UserOnboardingState = {
  currentStep: 'welcome',
  completedSteps: [],
  canProceed: true,
  userData: initialUserData,
  isLoading: false,
  error: null,
  isOptional: true
};

function onboardingReducer(state: UserOnboardingState, action: OnboardingAction): UserOnboardingState {
  switch (action.type) {
    case 'SET_CURRENT_STEP':
      const stepConfig = ONBOARDING_STEPS.find(s => s.id === action.payload);
      return {
        ...state,
        currentStep: action.payload,
        isOptional: stepConfig?.isOptional || false
      };
    case 'ADD_COMPLETED_STEP':
      if (!state.completedSteps.includes(action.payload)) {
        return {
          ...state,
          completedSteps: [...state.completedSteps, action.payload]
        };
      }
      return state;
    case 'SET_CAN_PROCEED':
      return { ...state, canProceed: action.payload };
    case 'UPDATE_USER_DATA':
      return {
        ...state,
        userData: { ...state.userData, ...action.payload }
      };
    case 'UPDATE_EXPERIENCE_DATA':
      return {
        ...state,
        userData: {
          ...state.userData,
          experienceData: { ...state.userData.experienceData, ...action.payload }
        }
      };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ESTIMATED_ELO':
      return {
        ...state,
        userData: { ...state.userData, estimatedElo: action.payload }
      };
    case 'LOAD_STATE':
      return { ...state, ...action.payload };
    case 'RESET_ONBOARDING':
      return initialState;
    default:
      return state;
  }
}

interface UserOnboardingProviderProps {
  children: React.ReactNode;
  skipForExistingUsers?: boolean;
}

export function UserOnboardingProvider({ 
  children, 
  skipForExistingUsers = true 
}: UserOnboardingProviderProps) {
  const [state, dispatch] = useReducer(onboardingReducer, initialState);
  const { user, updatePreferredPosition } = useAuth();

  // Load saved state on mount
  useEffect(() => {
    const savedState = loadOnboardingState();
    if (savedState) {
      dispatch({
        type: 'LOAD_STATE',
        payload: {
          currentStep: savedState.currentStep,
          completedSteps: savedState.completedSteps,
          userData: savedState.userData
        }
      });
    }
  }, []);

  // Save state when it changes
  useEffect(() => {
    if (state.currentStep !== 'welcome' || state.completedSteps.length > 0) {
      saveOnboardingState({
        currentStep: state.currentStep,
        completedSteps: state.completedSteps,
        userData: state.userData
      });
      saveCurrentStep(state.currentStep);
    }
  }, [state.currentStep, state.completedSteps, state.userData]);

  // Calculate ELO when experience data changes
  useEffect(() => {
    const estimatedElo = calculateEstimatedElo(state.userData.experienceData);
    if (estimatedElo !== state.userData.estimatedElo) {
      dispatch({ type: 'SET_ESTIMATED_ELO', payload: estimatedElo });
    }
  }, [state.userData.experienceData, state.userData.estimatedElo]);

  // Navigation functions
  const nextStep = useCallback(() => {
    const currentIndex = ONBOARDING_STEPS.findIndex(s => s.id === state.currentStep);
    if (currentIndex >= 0 && currentIndex < ONBOARDING_STEPS.length - 1) {
      const nextStep = ONBOARDING_STEPS[currentIndex + 1];
      if (nextStep) {
        dispatch({ type: 'ADD_COMPLETED_STEP', payload: state.currentStep });
        dispatch({ type: 'SET_CURRENT_STEP', payload: nextStep.id });
      }
    }
  }, [state.currentStep]);

  const previousStep = useCallback(() => {
    const currentIndex = ONBOARDING_STEPS.findIndex(s => s.id === state.currentStep);
    if (currentIndex > 0) {
      const prevStep = ONBOARDING_STEPS[currentIndex - 1];
      if (prevStep) {
        dispatch({ type: 'SET_CURRENT_STEP', payload: prevStep.id });
      }
    }
  }, [state.currentStep]);

  const goToStep = useCallback((step: OnboardingStep) => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: step });
  }, []);

  const skipStep = useCallback(() => {
    if (state.isOptional) {
      nextStep();
    }
  }, [state.isOptional, nextStep]);

  // Data update functions
  const updateUserData = useCallback((data: Partial<OnboardingUserData>) => {
    dispatch({ type: 'UPDATE_USER_DATA', payload: data });
  }, []);

  const updateExperienceData = useCallback((data: Partial<ExperienceAssessment>) => {
    dispatch({ type: 'UPDATE_EXPERIENCE_DATA', payload: data });
  }, []);

  const setProfilePicture = useCallback((file: File) => {
    dispatch({ type: 'UPDATE_USER_DATA', payload: { profilePictureFile: file } });
  }, []);

  const setPreferredPosition = useCallback((position: PreferredPosition) => {
    dispatch({ type: 'UPDATE_USER_DATA', payload: { preferredPosition: position } });
  }, []);

  // Control functions
  const setError = useCallback((error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  }, []);

  const setIsLoading = useCallback((loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  }, []);

  // Complete onboarding process
  const completeOnboarding = useCallback(async () => {
    if (!user) {
      setError('User not authenticated');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // Upload profile picture if provided
      if (state.userData.profilePictureFile) {
        const formData = new FormData();
        formData.append('file', state.userData.profilePictureFile);
        
        try {
          await apiClient.post('/users/me/profile-picture', formData);
        } catch (error) {
          console.warn('Failed to upload profile picture:', error);
          // Don't fail the entire onboarding for profile picture upload
        }
      }

      // Update preferred position if provided
      if (state.userData.preferredPosition) {
        try {
          await updatePreferredPosition(state.userData.preferredPosition);
        } catch (error) {
          console.warn('Failed to update preferred position:', error);
        }
      }

      // Update ELO rating if estimated
      if (state.userData.estimatedElo > 1.0) {
        try {
          await apiClient.put('/users/me', {
            elo_rating: state.userData.estimatedElo
          });
        } catch (error) {
          console.warn('Failed to update ELO rating:', error);
        }
      }

      // Mark onboarding as completed
      if (user.id) {
        markOnboardingCompleted(user.id);
      }
      clearOnboardingState();
      
      toast.success('Welcome to PadelGo! Your profile has been set up successfully.');
      
      // Navigate to complete step
      dispatch({ type: 'SET_CURRENT_STEP', payload: 'complete' });
    } catch (error) {
      console.error('Failed to complete onboarding:', error);
      setError('Failed to complete setup. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [user, state.userData, updatePreferredPosition, setError, setIsLoading]);

  const skipOnboarding = useCallback(() => {
    if (user && user.id) {
      markOnboardingCompleted(user.id);
      clearOnboardingState();
    }
  }, [user]);

  // Utility functions
  const getStepProgress = useCallback((): number => {
    const currentIndex = ONBOARDING_STEPS.findIndex(s => s.id === state.currentStep);
    const totalSteps = ONBOARDING_STEPS.length;
    return Math.round(((currentIndex + 1) / totalSteps) * 100);
  }, [state.currentStep]);

  const isStepCompleted = useCallback((step: OnboardingStep): boolean => {
    return state.completedSteps.includes(step);
  }, [state.completedSteps]);

  const canNavigateToStep = useCallback((step: OnboardingStep): boolean => {
    const stepIndex = ONBOARDING_STEPS.findIndex(s => s.id === step);
    const currentIndex = ONBOARDING_STEPS.findIndex(s => s.id === state.currentStep);
    
    // Can navigate backward or to completed steps
    return stepIndex <= currentIndex || isStepCompleted(step);
  }, [state.currentStep, isStepCompleted]);

  // Check if user should skip onboarding
  useEffect(() => {
    if (skipForExistingUsers && user && user.id && hasCompletedOnboarding(user.id)) {
      // User has already completed onboarding, don't show it again
      return;
    }
  }, [user, skipForExistingUsers]);

  const contextValue: UserOnboardingContextType = {
    ...state,
    nextStep,
    previousStep,
    goToStep,
    skipStep,
    updateUserData,
    updateExperienceData,
    setProfilePicture,
    setPreferredPosition,
    setError,
    setIsLoading,
    completeOnboarding,
    skipOnboarding,
    getStepProgress,
    isStepCompleted,
    canNavigateToStep
  };

  return (
    <UserOnboardingContext.Provider value={contextValue}>
      {children}
    </UserOnboardingContext.Provider>
  );
}

export function useUserOnboarding() {
  const context = useContext(UserOnboardingContext);
  if (context === undefined) {
    throw new Error('useUserOnboarding must be used within a UserOnboardingProvider');
  }
  return context;
}