"use client";

import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import { toast } from 'sonner';
import { GameOnboardingContextType, GameOnboardingState, OnboardingStep, AuthMode, GameInvitationInfo } from './types';

const GameOnboardingContext = createContext<GameOnboardingContextType | undefined>(undefined);

type GameOnboardingAction =
  | { type: 'SET_GAME_DATA'; payload: GameInvitationInfo }
  | { type: 'SET_CURRENT_STEP'; payload: OnboardingStep }
  | { type: 'SET_AUTH_MODE'; payload: AuthMode }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_GAME_JOINED'; payload: boolean }
  | { type: 'SET_INVITATION_TOKEN'; payload: string }
  | { type: 'RESET_FLOW' };

const initialState: GameOnboardingState = {
  invitationToken: null,
  gameData: null,
  currentStep: 'preview',
  authMode: 'login',
  isLoading: false,
  error: null,
  isGameJoined: false,
};

function gameOnboardingReducer(state: GameOnboardingState, action: GameOnboardingAction): GameOnboardingState {
  switch (action.type) {
    case 'SET_GAME_DATA':
      return { ...state, gameData: action.payload };
    case 'SET_CURRENT_STEP':
      return { ...state, currentStep: action.payload };
    case 'SET_AUTH_MODE':
      return { ...state, authMode: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_GAME_JOINED':
      return { ...state, isGameJoined: action.payload };
    case 'SET_INVITATION_TOKEN':
      return { ...state, invitationToken: action.payload };
    case 'RESET_FLOW':
      return { ...initialState };
    default:
      return state;
  }
}

interface GameOnboardingProviderProps {
  children: React.ReactNode;
  invitationToken?: string;
}

export function GameOnboardingProvider({ children, invitationToken: initialToken }: GameOnboardingProviderProps) {
  const [state, dispatch] = useReducer(gameOnboardingReducer, {
    ...initialState,
    invitationToken: initialToken || null,
  });
  
  const { user, accessToken } = useAuth();

  // Action creators
  const setGameData = useCallback((data: GameInvitationInfo) => {
    dispatch({ type: 'SET_GAME_DATA', payload: data });
  }, []);

  const setCurrentStep = useCallback((step: OnboardingStep) => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: step });
  }, []);

  const setAuthMode = useCallback((mode: AuthMode) => {
    dispatch({ type: 'SET_AUTH_MODE', payload: mode });
  }, []);

  const setError = useCallback((error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  }, []);

  const setIsLoading = useCallback((loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  }, []);

  // Main flow actions
  const loadGameData = useCallback(async (token: string) => {
    try {
      setIsLoading(true);
      setError(null);
      dispatch({ type: 'SET_INVITATION_TOKEN', payload: token });

      const response = await apiClient.get<GameInvitationInfo>(
        `/games/invitations/${token}/info`,
        {},
        null,
        false // Public endpoint
      );

      setGameData(response);
      
      // Determine initial step based on auth state and game status
      if (!response.is_valid || response.is_expired) {
        setCurrentStep('error');
        setError(response.is_expired ? 'This invitation has expired' : 'This invitation is invalid');
      } else if (response.is_full) {
        setCurrentStep('error');
        setError('This game is already full');
      } else if (user && accessToken) {
        setCurrentStep('preview'); // User is authenticated, show join option
      } else {
        setCurrentStep('preview'); // Show game preview with auth requirement
      }
    } catch (error) {
      console.error('Failed to load game data:', error);
      setCurrentStep('error');
      setError('Failed to load game information. Please check the invitation link.');
    } finally {
      setIsLoading(false);
    }
  }, [user, accessToken, setGameData, setCurrentStep, setError, setIsLoading]);

  const joinGame = useCallback(async () => {
    if (!state.invitationToken || !state.gameData || !accessToken) {
      setError('Missing required information to join game');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      setCurrentStep('joining');

      await apiClient.post(
        `/games/invitations/${state.invitationToken}/accept`,
        {}
      );

      dispatch({ type: 'SET_GAME_JOINED', payload: true });
      setCurrentStep('success');
      toast.success(`Successfully joined ${state.gameData.game.booking.court.name}!`);
    } catch (error) {
      console.error('Failed to join game:', error);
      setCurrentStep('error');
      setError('Failed to join the game. Please try again.');
      toast.error('Failed to join game');
    } finally {
      setIsLoading(false);
    }
  }, [state.invitationToken, state.gameData, accessToken, setIsLoading, setError, setCurrentStep]);

  const handleAuthSuccess = useCallback(async () => {
    // After successful authentication, automatically attempt to join the game
    if (state.gameData && state.gameData.can_join) {
      await joinGame();
    } else {
      setCurrentStep('preview');
    }
  }, [state.gameData, joinGame, setCurrentStep]);

  const resetFlow = useCallback(() => {
    dispatch({ type: 'RESET_FLOW' });
  }, []);

  // Save state to sessionStorage for recovery after page refresh during auth
  React.useEffect(() => {
    if (state.invitationToken && state.gameData) {
      sessionStorage.setItem('gameOnboardingState', JSON.stringify({
        invitationToken: state.invitationToken,
        gameData: state.gameData,
        currentStep: state.currentStep,
      }));
    }
  }, [state.invitationToken, state.gameData, state.currentStep]);

  // Restore state from sessionStorage on mount
  React.useEffect(() => {
    const savedState = sessionStorage.getItem('gameOnboardingState');
    if (savedState && !state.gameData) {
      try {
        const parsedState = JSON.parse(savedState);
        dispatch({ type: 'SET_INVITATION_TOKEN', payload: parsedState.invitationToken });
        dispatch({ type: 'SET_GAME_DATA', payload: parsedState.gameData });
        dispatch({ type: 'SET_CURRENT_STEP', payload: parsedState.currentStep });
      } catch (error) {
        console.error('Failed to restore game onboarding state:', error);
        sessionStorage.removeItem('gameOnboardingState');
      }
    }
  }, [state.gameData]);

  const contextValue: GameOnboardingContextType = {
    ...state,
    setGameData,
    setCurrentStep,
    setAuthMode,
    setError,
    setIsLoading,
    loadGameData,
    joinGame,
    resetFlow,
    handleAuthSuccess,
  };

  return (
    <GameOnboardingContext.Provider value={contextValue}>
      {children}
    </GameOnboardingContext.Provider>
  );
}

export function useGameOnboarding() {
  const context = useContext(GameOnboardingContext);
  if (context === undefined) {
    throw new Error('useGameOnboarding must be used within a GameOnboardingProvider');
  }
  return context;
}