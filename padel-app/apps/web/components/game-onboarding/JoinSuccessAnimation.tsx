"use client";

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Button } from '@workspace/ui/components/button';
import { Badge } from '@workspace/ui/components/badge';
import { useGameOnboarding } from './GameOnboardingProvider';
import { Trophy, Users, Calendar, MapPin, ExternalLink } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { format } from 'date-fns';

export function JoinSuccessAnimation() {
  const { gameData, currentStep } = useGameOnboarding();
  const router = useRouter();
  const [showConfetti, setShowConfetti] = useState(false);
  const [animationStep, setAnimationStep] = useState(0);

  useEffect(() => {
    if (currentStep === 'success') {
      // Trigger confetti animation
      setShowConfetti(true);
      
      // Animate the success message in steps
      const timer1 = setTimeout(() => setAnimationStep(1), 200);
      const timer2 = setTimeout(() => setAnimationStep(2), 600);
      const timer3 = setTimeout(() => setAnimationStep(3), 1000);
      
      // Remove confetti after animation
      const confettiTimer = setTimeout(() => setShowConfetti(false), 3000);
      
      return () => {
        clearTimeout(timer1);
        clearTimeout(timer2);
        clearTimeout(timer3);
        clearTimeout(confettiTimer);
      };
    }
  }, [currentStep]);

  if (currentStep !== 'success' || !gameData) {
    return null;
  }

  const { game } = gameData;
  const { booking } = game;
  const { court } = booking;

  const formatDateTime = (dateTime: string) => {
    return format(new Date(dateTime), 'EEEE, MMMM d • h:mm a');
  };

  const handleViewGame = () => {
    router.push(`/games/${game.id}`);
  };

  const handleViewBookings = () => {
    router.push('/bookings');
  };

  return (
    <div className="relative">
      {/* Confetti Effect */}
      {showConfetti && (
        <div className="fixed inset-0 pointer-events-none z-50">
          <div className="absolute inset-0 overflow-hidden">
            {[...Array(50)].map((_, i) => (
              <div
                key={i}
                className="absolute w-2 h-2 bg-primary rounded-full animate-bounce"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 2}s`,
                  animationDuration: `${1 + Math.random() * 2}s`,
                }}
              />
            ))}
          </div>
        </div>
      )}

      <Card className="w-full max-w-md mx-auto">
        <CardHeader className="text-center pb-2">
          {/* Success Icon Animation */}
          <div className="mx-auto mb-4">
            <div
              className={`w-16 h-16 bg-green-100 rounded-full flex items-center justify-center transition-all duration-500 ${
                animationStep >= 1 ? 'scale-100 opacity-100' : 'scale-0 opacity-0'
              }`}
            >
              <Trophy
                className={`h-8 w-8 text-green-600 transition-all duration-300 ${
                  animationStep >= 1 ? 'rotate-0' : 'rotate-45'
                }`}
              />
            </div>
          </div>

          <CardTitle
            className={`text-xl font-bold text-green-700 transition-all duration-500 ${
              animationStep >= 2 ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'
            }`}
          >
            You&apos;re In!
          </CardTitle>
          
          <p
            className={`text-muted-foreground transition-all duration-500 ${
              animationStep >= 2 ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'
            }`}
          >
            Successfully joined the game
          </p>
        </CardHeader>

        <CardContent
          className={`space-y-4 transition-all duration-500 ${
            animationStep >= 3 ? 'translate-y-0 opacity-100' : 'translate-y-6 opacity-0'
          }`}
        >
          {/* Game Details Summary */}
          <div className="bg-muted/50 rounded-lg p-4 space-y-3">
            <div className="flex items-center gap-2 text-sm">
              <MapPin className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="font-medium">{court.name}</p>
                <p className="text-muted-foreground">{court.club?.name}</p>
              </div>
            </div>

            <div className="flex items-center gap-2 text-sm">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span>{formatDateTime(booking.start_time)}</span>
            </div>

            <div className="flex items-center gap-2 text-sm">
              <Users className="h-4 w-4 text-muted-foreground" />
              <span>{(game.players?.filter(p => p.status === 'ACCEPTED') || []).length}/4 players</span>
            </div>

            <div className="flex justify-center">
              <Badge variant="default">
                {game.game_type.charAt(0) + game.game_type.slice(1).toLowerCase()} Game
              </Badge>
            </div>
          </div>

          {/* Next Steps */}
          <div className="space-y-3">
            <h4 className="font-medium text-sm">What&apos;s Next?</h4>
            
            <div className="space-y-2">
              <Button
                onClick={handleViewGame}
                className="w-full"
                variant="default"
              >
                <ExternalLink className="mr-2 h-4 w-4" />
                View Game Details
              </Button>
              
              <Button
                onClick={handleViewBookings}
                className="w-full"
                variant="outline"
              >
                View My Bookings
              </Button>
            </div>
          </div>

          {/* Pro Tips */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <h5 className="font-medium text-blue-900 text-sm mb-1">💡 Pro Tips</h5>
            <ul className="text-xs text-blue-700 space-y-1">
              <li>• Invite friends to fill remaining spots</li>
              <li>• Add the game to your calendar</li>
              <li>• Check the weather before game day</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}