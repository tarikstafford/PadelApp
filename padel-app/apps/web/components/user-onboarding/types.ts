export type OnboardingStep = 
  | 'welcome' 
  | 'position' 
  | 'experience' 
  | 'elo-estimation' 
  | 'features' 
  | 'complete';

export type PlayingFrequency = 'rarely' | 'monthly' | 'weekly' | 'daily';
export type SkillLevel = 1 | 2 | 3 | 4 | 5;
export type PreferredPosition = 'LEFT' | 'RIGHT';

export interface ExperienceAssessment {
  yearsPlaying: number;
  previousSports: string[];
  selfAssessedSkill: SkillLevel;
  playingFrequency: PlayingFrequency;
  competitiveExperience: boolean;
  tournamentParticipation: boolean;
  coachingExperience: boolean;
  injuryHistory?: boolean;
}

export interface OnboardingUserData {
  profilePictureFile?: File;
  profilePictureUrl?: string;
  preferredPosition?: PreferredPosition;
  experienceData: Partial<ExperienceAssessment>;
  estimatedElo: number;
  skipOptionalSteps: boolean;
}

export interface UserOnboardingState {
  currentStep: OnboardingStep;
  completedSteps: OnboardingStep[];
  canProceed: boolean;
  userData: OnboardingUserData;
  isLoading: boolean;
  error: string | null;
  isOptional: boolean;
}

export interface UserOnboardingContextType extends UserOnboardingState {
  // Navigation actions
  nextStep: () => void;
  previousStep: () => void;
  goToStep: (step: OnboardingStep) => void;
  skipStep: () => void;
  
  // Data actions
  updateUserData: (data: Partial<OnboardingUserData>) => void;
  updateExperienceData: (data: Partial<ExperienceAssessment>) => void;
  setProfilePicture: (file: File) => void;
  setPreferredPosition: (position: PreferredPosition) => void;
  
  // Flow control
  setError: (error: string | null) => void;
  setIsLoading: (loading: boolean) => void;
  completeOnboarding: () => Promise<void>;
  skipOnboarding: () => void;
  
  // Utility
  getStepProgress: () => number;
  isStepCompleted: (step: OnboardingStep) => boolean;
  canNavigateToStep: (step: OnboardingStep) => boolean;
}

export interface StepConfig {
  id: OnboardingStep;
  title: string;
  description: string;
  isOptional: boolean;
  estimatedTime: string;
  icon: string;
}

export const ONBOARDING_STEPS: StepConfig[] = [
  {
    id: 'welcome',
    title: 'Welcome to PadelGo',
    description: 'Set up your profile picture and learn about the app',
    isOptional: true,
    estimatedTime: '2 min',
    icon: '👋'
  },
  {
    id: 'position',
    title: 'Playing Position',
    description: 'Choose your preferred court position',
    isOptional: false,
    estimatedTime: '1 min',
    icon: '🎾'
  },
  {
    id: 'experience',
    title: 'Experience Assessment',
    description: 'Tell us about your padel background',
    isOptional: false,
    estimatedTime: '3 min',
    icon: '📋'
  },
  {
    id: 'elo-estimation',
    title: 'Skill Rating',
    description: 'Your estimated ELO rating and what it means',
    isOptional: false,
    estimatedTime: '2 min',
    icon: '🏆'
  },
  {
    id: 'features',
    title: 'App Features',
    description: 'Discover what you can do with PadelGo',
    isOptional: true,
    estimatedTime: '3 min',
    icon: '✨'
  },
  {
    id: 'complete',
    title: 'All Set!',
    description: 'Start playing and connecting with the community',
    isOptional: false,
    estimatedTime: '1 min',
    icon: '🎉'
  }
];