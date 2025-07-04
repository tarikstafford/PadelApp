import { OnboardingStep, OnboardingUserData } from '../types';

const STORAGE_KEY = 'padelgo_onboarding_state';
const STEP_STORAGE_KEY = 'padelgo_onboarding_step';

export interface StoredOnboardingState {
  currentStep: OnboardingStep;
  completedSteps: OnboardingStep[];
  userData: OnboardingUserData;
  timestamp: number;
}

/**
 * Save onboarding state to sessionStorage
 */
export function saveOnboardingState(state: Omit<StoredOnboardingState, 'timestamp'>): void {
  try {
    const stateToSave: StoredOnboardingState = {
      ...state,
      timestamp: Date.now()
    };
    
    // Don't store the File object, just the URL if it exists
    if (stateToSave.userData.profilePictureFile) {
      stateToSave.userData.profilePictureUrl = URL.createObjectURL(stateToSave.userData.profilePictureFile);
      delete stateToSave.userData.profilePictureFile;
    }
    
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(stateToSave));
  } catch (error) {
    console.warn('Failed to save onboarding state:', error);
  }
}

/**
 * Load onboarding state from sessionStorage
 */
export function loadOnboardingState(): StoredOnboardingState | null {
  try {
    const stored = sessionStorage.getItem(STORAGE_KEY);
    if (!stored) return null;
    
    const state: StoredOnboardingState = JSON.parse(stored);
    
    // Check if state is expired (24 hours)
    const isExpired = Date.now() - state.timestamp > 24 * 60 * 60 * 1000;
    if (isExpired) {
      clearOnboardingState();
      return null;
    }
    
    return state;
  } catch (error) {
    console.warn('Failed to load onboarding state:', error);
    clearOnboardingState();
    return null;
  }
}

/**
 * Clear onboarding state from storage
 */
export function clearOnboardingState(): void {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
    sessionStorage.removeItem(STEP_STORAGE_KEY);
  } catch (error) {
    console.warn('Failed to clear onboarding state:', error);
  }
}

/**
 * Save current step for quick recovery
 */
export function saveCurrentStep(step: OnboardingStep): void {
  try {
    sessionStorage.setItem(STEP_STORAGE_KEY, step);
  } catch (error) {
    console.warn('Failed to save current step:', error);
  }
}

/**
 * Load current step
 */
export function loadCurrentStep(): OnboardingStep | null {
  try {
    return sessionStorage.getItem(STEP_STORAGE_KEY) as OnboardingStep;
  } catch (error) {
    console.warn('Failed to load current step:', error);
    return null;
  }
}

/**
 * Mark onboarding as completed in localStorage (persistent)
 */
export function markOnboardingCompleted(userId: number): void {
  try {
    const completedUsers = getCompletedUsers();
    completedUsers.add(userId);
    localStorage.setItem('padelgo_completed_onboarding', JSON.stringify(Array.from(completedUsers)));
  } catch (error) {
    console.warn('Failed to mark onboarding completed:', error);
  }
}

/**
 * Check if user has completed onboarding
 */
export function hasCompletedOnboarding(userId: number): boolean {
  try {
    const completedUsers = getCompletedUsers();
    return completedUsers.has(userId);
  } catch (error) {
    console.warn('Failed to check onboarding completion:', error);
    return false;
  }
}

/**
 * Get set of users who have completed onboarding
 */
function getCompletedUsers(): Set<number> {
  try {
    const stored = localStorage.getItem('padelgo_completed_onboarding');
    if (!stored) return new Set();
    
    const userIds: number[] = JSON.parse(stored);
    return new Set(userIds);
  } catch (error) {
    console.warn('Failed to get completed users:', error);
    return new Set();
  }
}