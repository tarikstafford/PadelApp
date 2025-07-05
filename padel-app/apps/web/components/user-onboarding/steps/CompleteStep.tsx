"use client";

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Button } from '@workspace/ui/components/button';
import { Badge } from '@workspace/ui/components/badge';
import { useUserOnboarding } from '../UserOnboardingProvider';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { 
  CheckCircle, 
  Sparkles, 
  Trophy, 
  MapPin, 
  Users, 
  Calendar,
  Star,
  ArrowRight,
  Gift
} from 'lucide-react';
import { getEloSkillLevel } from '../utils/eloEstimation';

export function CompleteStep() {
  const { userData } = useUserOnboarding();
  const { user } = useAuth();
  const router = useRouter();
  const [showConfetti, setShowConfetti] = useState(false);
  const [animationStep, setAnimationStep] = useState(0);

  const skillLevel = getEloSkillLevel(userData.estimatedElo);

  useEffect(() => {
    // Trigger confetti animation
    setShowConfetti(true);
    
    // Animate the success message in steps
    const timer1 = setTimeout(() => setAnimationStep(1), 300);
    const timer2 = setTimeout(() => setAnimationStep(2), 700);
    const timer3 = setTimeout(() => setAnimationStep(3), 1100);
    
    // Remove confetti after animation
    const confettiTimer = setTimeout(() => setShowConfetti(false), 4000);
    
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(confettiTimer);
    };
  }, []);

  const handleGetStarted = () => {
    router.push('/discover');
  };

  const handleViewProfile = () => {
    router.push('/profile');
  };

  const handleBrowseGames = () => {
    router.push('/games/public');
  };

  const getDisplayName = () => {
    if (user?.full_name) return user.full_name.split(' ')[0];
    if (user?.email) return user.email.split('@')[0];
    return 'there';
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
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

      {/* Success Header */}
      <div className="text-center space-y-4">
        <div
          className={`mx-auto mb-4 transition-all duration-500 ${
            animationStep >= 1 ? 'scale-100 opacity-100' : 'scale-0 opacity-0'
          }`}
        >
          <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="h-12 w-12 text-green-600" />
          </div>
        </div>

        <div
          className={`space-y-2 transition-all duration-500 ${
            animationStep >= 2 ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'
          }`}
        >
          <h1 className="text-3xl font-bold text-green-700">
            🎉 Welcome to PadelGo, {getDisplayName()}!
          </h1>
          <p className="text-lg text-muted-foreground">
            Your profile is all set up and you&apos;re ready to start your padel journey!
          </p>
        </div>
      </div>

      {/* Profile Summary */}
      <div
        className={`transition-all duration-500 ${
          animationStep >= 3 ? 'translate-y-0 opacity-100' : 'translate-y-6 opacity-0'
        }`}
      >
        <Card className="border-2 border-green-200 bg-green-50 dark:bg-green-950 dark:border-green-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-800 dark:text-green-200">
              <Star className="h-5 w-5" />
              Your Profile Summary
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              {/* ELO Rating */}
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center">
                  <Trophy className="h-6 w-6 text-white" />
                </div>
                <div>
                  <p className="font-medium">Estimated ELO Rating</p>
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-bold text-primary">
                      {userData.estimatedElo.toFixed(1)}
                    </span>
                    <Badge variant="outline">
                      {skillLevel.title}
                    </Badge>
                  </div>
                  {userData.estimatedElo > 1.0 && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Adjustment request submitted
                    </p>
                  )}
                </div>
              </div>

              {/* Position */}
              {userData.preferredPosition && (
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center">
                    <Users className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="font-medium">Preferred Position</p>
                    <p className="text-muted-foreground">
                      {userData.preferredPosition === 'LEFT' ? 'Left Side (Defense)' : 'Right Side (Attack)'}
                    </p>
                  </div>
                </div>
              )}

              {/* Profile Picture */}
              {userData.profilePictureFile && (
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-purple-100 text-purple-600 rounded-lg flex items-center justify-center">
                    <Gift className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="font-medium">Profile Picture</p>
                    <p className="text-muted-foreground">Uploaded successfully!</p>
                  </div>
                </div>
              )}

              {/* Experience */}
              {userData.experienceData.yearsPlaying !== undefined && (
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-orange-100 text-orange-600 rounded-lg flex items-center justify-center">
                    <Calendar className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="font-medium">Experience</p>
                    <p className="text-muted-foreground">
                      {userData.experienceData.yearsPlaying === 0 
                        ? 'New to padel' 
                        : `${userData.experienceData.yearsPlaying} years playing`}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* What's Next */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            What&apos;s Next?
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-muted-foreground">
              Now that your profile is set up, here are some great ways to get started:
            </p>
            
            <div className="grid gap-4 md:grid-cols-3">
              <Button
                onClick={handleGetStarted}
                className="h-auto p-4 flex-col gap-2"
                variant="outline"
              >
                <MapPin className="h-6 w-6" />
                <div className="text-center">
                  <div className="font-medium">Find Courts</div>
                  <div className="text-xs text-muted-foreground">
                    Discover courts near you
                  </div>
                </div>
              </Button>
              
              <Button
                onClick={handleBrowseGames}
                className="h-auto p-4 flex-col gap-2"
                variant="outline"
              >
                <Users className="h-6 w-6" />
                <div className="text-center">
                  <div className="font-medium">Join Games</div>
                  <div className="text-xs text-muted-foreground">
                    Connect with players
                  </div>
                </div>
              </Button>
              
              <Button
                onClick={handleViewProfile}
                className="h-auto p-4 flex-col gap-2"
                variant="outline"
              >
                <Trophy className="h-6 w-6" />
                <div className="text-center">
                  <div className="font-medium">View Profile</div>
                  <div className="text-xs text-muted-foreground">
                    Track your progress
                  </div>
                </div>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Welcome Tips */}
      <Card className="bg-blue-50 border-blue-200 dark:bg-blue-950 dark:border-blue-800">
        <CardContent className="pt-6">
          <div className="space-y-3">
            <h4 className="font-medium text-blue-900 dark:text-blue-100">
              💡 Pro Tips for New Members
            </h4>
            <ul className="space-y-2 text-sm text-blue-700 dark:text-blue-200">
              <li className="flex items-start gap-2">
                <div className="w-1 h-1 bg-current rounded-full mt-2" />
                You&apos;ll start with a base rating of 1.0 that adjusts as you play
              </li>
              <li className="flex items-start gap-2">
                <div className="w-1 h-1 bg-current rounded-full mt-2" />
                Your ELO rating will adjust automatically based on game results
              </li>
              <li className="flex items-start gap-2">
                <div className="w-1 h-1 bg-current rounded-full mt-2" />
                Don&apos;t hesitate to reach out to other players - the community is welcoming!
              </li>
              <li className="flex items-start gap-2">
                <div className="w-1 h-1 bg-current rounded-full mt-2" />
                You can always update your preferences in your profile settings
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Final CTA */}
      <div className="text-center pt-6">
        <Button onClick={handleGetStarted} size="lg" className="px-8">
          Start Playing
          <ArrowRight className="ml-2 h-5 w-5" />
        </Button>
        <p className="text-sm text-muted-foreground mt-2">
          Ready to discover courts and join your first game!
        </p>
      </div>
    </div>
  );
}