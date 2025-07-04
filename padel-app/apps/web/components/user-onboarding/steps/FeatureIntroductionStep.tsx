"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Button } from '@workspace/ui/components/button';
import { Badge } from '@workspace/ui/components/badge';
import { useUserOnboarding } from '../UserOnboardingProvider';
import { 
  MapPin, 
  Calendar, 
  Users, 
  Trophy, 
  TrendingUp, 
  UserPlus,
  ArrowRight,
  Sparkles,
  Play,
  CheckCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';

const FEATURES = [
  {
    id: 'discover',
    title: 'Discover Courts & Games',
    description: 'Find padel courts near you and join games with players of your skill level.',
    icon: MapPin,
    color: 'blue',
    highlights: [
      'Search courts by location',
      'Filter by skill level and time',
      'Real-time availability',
      'Court photos and details'
    ],
    action: 'Browse Courts',
    path: '/discover'
  },
  {
    id: 'book',
    title: 'Book & Play',
    description: 'Reserve courts instantly and organize games with friends or new players.',
    icon: Calendar,
    color: 'green',
    highlights: [
      'Quick court booking',
      'Invite friends to games',
      'Join public games',
      'Flexible scheduling'
    ],
    action: 'View Bookings',
    path: '/bookings'
  },
  {
    id: 'compete',
    title: 'Compete in Tournaments',
    description: 'Participate in tournaments matched to your skill level and climb the rankings.',
    icon: Trophy,
    color: 'yellow',
    highlights: [
      'Skill-based tournaments',
      'Automated bracket generation',
      'Tournament history',
      'Achievement tracking'
    ],
    action: 'Join Tournaments',
    path: '/tournaments'
  },
  {
    id: 'progress',
    title: 'Track Your Progress',
    description: 'Monitor your ELO rating, game history, and improvement over time.',
    icon: TrendingUp,
    color: 'purple',
    highlights: [
      'ELO rating tracking',
      'Game statistics',
      'Performance insights',
      'Achievement badges'
    ],
    action: 'View Profile',
    path: '/profile'
  },
  {
    id: 'community',
    title: 'Build Your Network',
    description: 'Connect with other players, form teams, and grow your padel community.',
    icon: Users,
    color: 'indigo',
    highlights: [
      'Player connections',
      'Team formation',
      'Community leaderboards',
      'Social features'
    ],
    action: 'Find Teams',
    path: '/teams'
  }
];

export function FeatureIntroductionStep() {
  const { nextStep, skipStep, completeOnboarding } = useUserOnboarding();
  const [activeFeature, setActiveFeature] = useState(0);
  const [viewedFeatures, setViewedFeatures] = useState<Set<number>>(new Set([0]));

  const handleFeatureClick = (index: number) => {
    setActiveFeature(index);
    setViewedFeatures(prev => new Set([...prev, index]));
  };

  const handleNext = () => {
    if (activeFeature < FEATURES.length - 1) {
      handleFeatureClick(activeFeature + 1);
    } else {
      completeOnboarding();
    }
  };

  const handlePrevious = () => {
    if (activeFeature > 0) {
      handleFeatureClick(activeFeature - 1);
    }
  };

  const currentFeature = FEATURES[activeFeature];

  if (!currentFeature) {
    return null;
  }

  const Icon = currentFeature.icon;

  const getColorClasses = (color: string) => {
    const colorMap = {
      blue: 'from-blue-500 to-blue-600 text-white',
      green: 'from-green-500 to-green-600 text-white',
      yellow: 'from-yellow-500 to-yellow-600 text-white',
      purple: 'from-purple-500 to-purple-600 text-white',
      indigo: 'from-indigo-500 to-indigo-600 text-white'
    };
    return colorMap[color as keyof typeof colorMap] || colorMap.blue;
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Sparkles className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold">Discover PadelGo Features</h1>
        </div>
        <p className="text-muted-foreground">
          Take a quick tour of what you can do with PadelGo to enhance your padel experience.
        </p>
      </div>

      {/* Feature Navigation */}
      <div className="flex justify-center mb-8">
        <div className="flex gap-2 p-2 bg-muted rounded-lg">
          {FEATURES.map((feature, index) => {
            const FeatureIcon = feature.icon;
            const isActive = index === activeFeature;
            const isViewed = viewedFeatures.has(index);
            
            return (
              <button
                key={feature.id}
                onClick={() => handleFeatureClick(index)}
                className={cn(
                  "flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200",
                  isActive 
                    ? "bg-primary text-primary-foreground shadow-sm" 
                    : "hover:bg-background",
                  isViewed && !isActive && "bg-background border"
                )}
              >
                <FeatureIcon className="h-4 w-4" />
                {isViewed && !isActive && <CheckCircle className="h-3 w-3 text-green-500" />}
                <span className="hidden sm:inline">{feature.title.split(' ')[0]}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Feature Display */}
      <Card className="border-2 border-primary/20">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={cn(
                "w-16 h-16 rounded-xl flex items-center justify-center bg-gradient-to-br",
                getColorClasses(currentFeature.color)
              )}>
                <Icon className="h-8 w-8" />
              </div>
              <div>
                <CardTitle className="text-2xl">{currentFeature.title}</CardTitle>
                <p className="text-muted-foreground mt-1">{currentFeature.description}</p>
              </div>
            </div>
            <Badge variant="outline">
              {activeFeature + 1} of {FEATURES.length}
            </Badge>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Feature Highlights */}
          <div>
            <h4 className="font-medium mb-3">Key Features:</h4>
            <div className="grid gap-3 md:grid-cols-2">
              {currentFeature.highlights.map((highlight, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary rounded-full flex-shrink-0" />
                  <span className="text-sm">{highlight}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Interactive Demo Area */}
          <div className="bg-muted/50 rounded-lg p-6 text-center">
            <div className="space-y-3">
              <Play className="h-8 w-8 mx-auto text-muted-foreground" />
              <p className="text-sm text-muted-foreground">
                Ready to try {currentFeature.title.toLowerCase()}?
              </p>
              <Button variant="outline" size="sm">
                {currentFeature.action}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UserPlus className="h-5 w-5" />
            Get Started Right Away
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center mx-auto">
                <MapPin className="h-6 w-6" />
              </div>
              <h4 className="font-medium">Find Your First Game</h4>
              <p className="text-sm text-muted-foreground">
                Browse courts near you and join a game that matches your skill level
              </p>
            </div>
            
            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-green-100 text-green-600 rounded-lg flex items-center justify-center mx-auto">
                <Users className="h-6 w-6" />
              </div>
              <h4 className="font-medium">Connect with Players</h4>
              <p className="text-sm text-muted-foreground">
                Join the community and start building your padel network
              </p>
            </div>
            
            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-purple-100 text-purple-600 rounded-lg flex items-center justify-center mx-auto">
                <Trophy className="h-6 w-6" />
              </div>
              <h4 className="font-medium">Enter a Tournament</h4>
              <p className="text-sm text-muted-foreground">
                Challenge yourself in skill-appropriate tournaments
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between items-center pt-6">
        <div className="flex gap-2">
          <Button variant="outline" onClick={skipStep}>
            Skip Tour
          </Button>
          {activeFeature > 0 && (
            <Button variant="outline" onClick={handlePrevious}>
              Previous
            </Button>
          )}
        </div>
        
        <div className="flex items-center gap-3">
          <span className="text-sm text-muted-foreground">
            {activeFeature + 1} of {FEATURES.length}
          </span>
          <Button onClick={handleNext} size="lg">
            {activeFeature === FEATURES.length - 1 ? (
              'Complete Setup'
            ) : (
              <>
                Next Feature
                <ArrowRight className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}