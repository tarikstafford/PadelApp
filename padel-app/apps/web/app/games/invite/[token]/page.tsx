'use client';

import { useParams } from 'next/navigation';
import { useEffect } from 'react';
import { GameOnboardingProvider, GameOnboardingFlow, useGameOnboarding } from '@/components/game-onboarding';

function GameInvitePageContent() {
  const params = useParams();
  const { loadGameData } = useGameOnboarding();
  const token = params.token as string;

  useEffect(() => {
    if (token) {
      loadGameData(token);
    }
  }, [token, loadGameData]);

  return <GameOnboardingFlow />;
}

export default function GameInvitePage() {
  const params = useParams();
  const token = params.token as string;

  return (
    <GameOnboardingProvider invitationToken={token}>
      <GameInvitePageContent />
    </GameOnboardingProvider>
  );
}