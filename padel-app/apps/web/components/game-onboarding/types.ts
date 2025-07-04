import { Game, User } from "@/lib/types";

export interface GameInvitationInfo {
  game: Game;
  creator: User;
  invitation_token: string;
  is_valid: boolean;
  is_expired: boolean;
  is_full: boolean;
  can_join: boolean;
  expires_at: string;
}

export type OnboardingStep = 'preview' | 'auth' | 'joining' | 'success' | 'error';

export type AuthMode = 'login' | 'register';

export interface GameOnboardingState {
  invitationToken: string | null;
  gameData: GameInvitationInfo | null;
  currentStep: OnboardingStep;
  authMode: AuthMode;
  isLoading: boolean;
  error: string | null;
  isGameJoined: boolean;
}

export interface GameOnboardingContextType extends GameOnboardingState {
  // Actions
  setGameData: (data: GameInvitationInfo) => void;
  setCurrentStep: (step: OnboardingStep) => void;
  setAuthMode: (mode: AuthMode) => void;
  setError: (error: string | null) => void;
  setIsLoading: (loading: boolean) => void;
  
  // Main flow actions
  loadGameData: (token: string) => Promise<void>;
  joinGame: () => Promise<void>;
  resetFlow: () => void;
  
  // Auth integration
  handleAuthSuccess: () => Promise<void>;
}