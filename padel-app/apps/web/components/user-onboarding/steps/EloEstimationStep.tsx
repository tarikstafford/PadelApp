"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Button } from '@workspace/ui/components/button';
import { Badge } from '@workspace/ui/components/badge';
import { useUserOnboarding } from '../UserOnboardingProvider';
import { getEloSkillLevel, getEloExplanation } from '../utils/eloEstimation';
import { Trophy, TrendingUp, Users, Calendar, Target, Info } from 'lucide-react';

export function EloEstimationStep() {
  const { userData, nextStep } = useUserOnboarding();
  const { estimatedElo, experienceData } = userData;
  
  const skillLevel = getEloSkillLevel(estimatedElo);
  const explanation = getEloExplanation(experienceData, estimatedElo);

  const getProgressColor = (elo: number) => {
    if (elo >= 4.0) return 'bg-purple-500';
    if (elo >= 3.0) return 'bg-blue-500';
    if (elo >= 2.0) return 'bg-green-500';
    if (elo >= 1.5) return 'bg-yellow-500';
    return 'bg-orange-500';
  };

  const getProgressWidth = (elo: number) => {
    // Scale ELO (1.0-7.0) to percentage (0-100%)
    return Math.min(100, Math.max(0, ((elo - 1.0) / 6.0) * 100));
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Your Estimated Skill Rating</h1>
        <p className="text-muted-foreground">
          Based on your experience, here&apos;s your starting ELO rating and what it means.
        </p>
      </div>

      {/* Main Rating Card */}
      <Card className="border-2 border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
        <CardHeader className="text-center pb-4">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Trophy className="h-8 w-8 text-primary" />
            <CardTitle className="text-2xl">Your ELO Rating</CardTitle>
          </div>
          
          <div className="space-y-4">
            <div className="text-6xl font-bold text-primary">
              {estimatedElo.toFixed(1)}
            </div>
            
            <Badge 
              variant="secondary" 
              className={`text-lg px-4 py-2 bg-${skillLevel.color}-100 text-${skillLevel.color}-800 border-${skillLevel.color}-200`}
            >
              Level {skillLevel.level} - {skillLevel.title}
            </Badge>
            
            <p className="text-muted-foreground max-w-md mx-auto">
              {skillLevel.description}
            </p>
          </div>
        </CardHeader>

        <CardContent>
          {/* Rating Scale */}
          <div className="space-y-3">
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Beginner (1.0)</span>
              <span>Professional (7.0)</span>
            </div>
            <div className="relative w-full h-3 bg-muted rounded-full overflow-hidden">
              <div 
                className={`h-full ${getProgressColor(estimatedElo)} transition-all duration-1000 ease-out`}
                style={{ width: `${getProgressWidth(estimatedElo)}%` }}
              />
              <div 
                className="absolute top-0 w-1 h-full bg-white border border-gray-300"
                style={{ left: `${getProgressWidth(estimatedElo)}%` }}
              />
            </div>
            <div className="text-center text-sm text-muted-foreground">
              You&apos;re in the {skillLevel.title} category
            </div>
          </div>
        </CardContent>
      </Card>

      {/* How We Calculated This */}
      {explanation.factors.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              How We Calculated This
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Your rating is based on the following factors:
              </p>
              <ul className="space-y-2">
                {explanation.factors.map((factor, index) => (
                  <li key={index} className="flex items-center gap-2 text-sm">
                    <div className="w-2 h-2 bg-primary rounded-full flex-shrink-0" />
                    {factor}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      )}

      {/* What This Means */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            What This Means for You
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <h4 className="font-medium flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-green-600" />
                Game Matching
              </h4>
              <p className="text-sm text-muted-foreground">
                You&apos;ll be matched with players of similar skill level for fair and competitive games.
              </p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium flex items-center gap-2">
                <Calendar className="h-4 w-4 text-blue-600" />
                Tournament Categories
              </h4>
              <p className="text-sm text-muted-foreground">
                You&apos;ll compete in tournaments appropriate for your skill level.
              </p>
            </div>
          </div>
          
          <div className="space-y-3 pt-2">
            <h4 className="font-medium">Recommendations for you:</h4>
            <ul className="space-y-2">
              {explanation.recommendations.map((rec, index) => (
                <li key={index} className="flex items-start gap-2 text-sm">
                  <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0" />
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Next Steps */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Your Next Steps
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {explanation.nextSteps.map((step, index) => (
              <li key={index} className="flex items-start gap-2 text-sm">
                <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0" />
                {step}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Important Note */}
      <Card className="bg-amber-50 border-amber-200 dark:bg-amber-950 dark:border-amber-800">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <Info className="h-5 w-5 text-amber-600 mt-0.5" />
            <div className="space-y-2">
              <h4 className="font-medium text-amber-900 dark:text-amber-100">
                Important Note
              </h4>
              <p className="text-sm text-amber-700 dark:text-amber-200">
                This is your starting rating based on your experience. As you play games, your ELO will 
                automatically adjust based on your actual performance. Don&apos;t worry if it doesn&apos;t feel exactly right - 
                it will become more accurate over time!
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between items-center pt-6">
        <div className="text-sm text-muted-foreground">
          Your rating: <span className="font-medium text-primary">{estimatedElo.toFixed(1)}</span>
        </div>
        <Button onClick={nextStep} size="lg">
          Continue Setup
        </Button>
      </div>
    </div>
  );
}