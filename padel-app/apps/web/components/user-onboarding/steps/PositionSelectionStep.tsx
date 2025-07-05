"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Button } from '@workspace/ui/components/button';
import { RadioGroup, RadioGroupItem } from '@workspace/ui/components/radio-group';
import { Label } from '@workspace/ui/components/label';
import { useUserOnboarding } from '../UserOnboardingProvider';
import { PreferredPosition } from '../types';
import { Target, Shield, Sword, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

const POSITION_INFO = {
  LEFT: {
    title: 'Left Side (Defense)',
    icon: Shield,
    primaryRole: 'Defensive Player',
    description: 'Controls the back of the court, focuses on retrieving difficult shots and setting up attacks',
    characteristics: [
      'Strong defensive skills and court coverage',
      'Excellent retrieving and lobbing abilities',
      'Strategic thinking and game management',
      'Steady and consistent play style'
    ],
    idealFor: [
      'Players who enjoy strategic gameplay',
      'Those with strong court awareness',
      'Players who prefer consistency over power',
      'Tennis players transitioning to padel'
    ],
    color: 'blue'
  },
  RIGHT: {
    title: 'Right Side (Attack)',
    icon: Sword,
    primaryRole: 'Attacking Player',
    description: 'Dominates the net area, focuses on finishing points and putting pressure on opponents',
    characteristics: [
      'Aggressive net play and volleys',
      'Strong smash and finishing abilities',
      'Quick reflexes and anticipation',
      'Decisive and dynamic play style'
    ],
    idealFor: [
      'Players who enjoy aggressive gameplay',
      'Those with strong hand-eye coordination',
      'Players who like to control the pace',
      'Athletes with quick reflexes'
    ],
    color: 'red'
  }
};

export function PositionSelectionStep() {
  const { userData, setPreferredPosition, nextStep, setError } = useUserOnboarding();
  const [selectedPosition, setSelectedPosition] = useState<PreferredPosition | undefined>(userData.preferredPosition);
  const [canProceed, setCanProceed] = useState(false);

  useEffect(() => {
    setCanProceed(selectedPosition !== undefined);
  }, [selectedPosition]);

  const handlePositionChange = (value: string) => {
    const position = value as PreferredPosition;
    setSelectedPosition(position);
    setPreferredPosition(position);
  };

  const handleNext = () => {
    if (!selectedPosition) {
      setError('Please select your preferred playing position.');
      return;
    }
    
    setError(null);
    nextStep();
  };

  const handleSkip = () => {
    setError(null);
    nextStep();
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Choose Your Playing Position</h1>
        <p className="text-muted-foreground">
          In padel, each player has a preferred side of the court. Select the position that best matches your playing style.
        </p>
      </div>

      {/* Court Diagram */}
      <Card className="bg-green-50 border-green-200 dark:bg-green-950 dark:border-green-800">
        <CardHeader>
          <CardTitle className="text-center flex items-center justify-center gap-2">
            <Target className="h-5 w-5" />
            Padel Court Positions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative max-w-md mx-auto">
            {/* Court Diagram */}
            <div className="relative bg-green-100 dark:bg-green-900 border-2 border-green-300 dark:border-green-700 rounded-lg p-4 aspect-[3/2]">
              {/* Net */}
              <div className="absolute top-1/2 left-0 right-0 h-1 bg-white transform -translate-y-0.5" />
              <div className="absolute top-1/2 left-1/2 w-1 h-8 bg-white transform -translate-x-0.5 -translate-y-4" />
              
              {/* Court Lines */}
              <div className="absolute inset-2 border border-white rounded opacity-50" />
              <div className="absolute top-2 bottom-1/2 left-2 right-2 border border-white opacity-30" />
              <div className="absolute top-1/2 bottom-2 left-2 right-2 border border-white opacity-30" />
              
              {/* Position Areas */}
              <div className="absolute top-2 bottom-1/2 left-2 right-1/2 flex items-center justify-center">
                <div className="bg-blue-500/20 border-2 border-blue-500 rounded-lg p-2 text-center">
                  <Shield className="h-6 w-6 mx-auto mb-1 text-blue-600" />
                  <div className="text-xs font-medium text-blue-800 dark:text-blue-200">LEFT</div>
                  <div className="text-xs text-blue-600">Defense</div>
                </div>
              </div>
              
              <div className="absolute top-2 bottom-1/2 left-1/2 right-2 flex items-center justify-center">
                <div className="bg-red-500/20 border-2 border-red-500 rounded-lg p-2 text-center">
                  <Sword className="h-6 w-6 mx-auto mb-1 text-red-600" />
                  <div className="text-xs font-medium text-red-800 dark:text-red-200">RIGHT</div>
                  <div className="text-xs text-red-600">Attack</div>
                </div>
              </div>
              
              {/* Opponent Side */}
              <div className="absolute top-1/2 bottom-2 left-2 right-2 flex items-center justify-center opacity-50">
                <div className="text-xs text-muted-foreground">Opponent Side</div>
              </div>
            </div>
            
            <p className="text-xs text-center mt-2 text-muted-foreground">
              Your side of the court (you&apos;ll play on both sides during a match)
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Position Selection */}
      <RadioGroup
        value={selectedPosition}
        onValueChange={handlePositionChange}
        className="space-y-4"
      >
        {Object.entries(POSITION_INFO).map(([position, info]) => {
          const Icon = info.icon;
          const isSelected = selectedPosition === position;
          
          return (
            <Card 
              key={position}
              className={cn(
                "transition-all duration-200 cursor-pointer hover:shadow-md",
                isSelected && "ring-2 ring-primary border-primary/50 bg-primary/5"
              )}
              onClick={() => handlePositionChange(position)}
            >
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <RadioGroupItem
                    value={position}
                    id={position}
                    className="mt-1"
                  />
                  
                  <div className="flex-1 space-y-4">
                    {/* Header */}
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        "w-12 h-12 rounded-lg flex items-center justify-center",
                        info.color === 'blue' ? 'bg-blue-100 text-blue-600' : 'bg-red-100 text-red-600'
                      )}>
                        <Icon className="h-6 w-6" />
                      </div>
                      <div>
                        <Label htmlFor={position} className="text-lg font-semibold cursor-pointer">
                          {info.title}
                        </Label>
                        <p className={cn(
                          "text-sm font-medium",
                          info.color === 'blue' ? 'text-blue-600' : 'text-red-600'
                        )}>
                          {info.primaryRole}
                        </p>
                      </div>
                    </div>
                    
                    {/* Description */}
                    <p className="text-muted-foreground">
                      {info.description}
                    </p>
                    
                    {/* Characteristics */}
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium mb-2">Key Characteristics:</h4>
                        <ul className="text-sm text-muted-foreground space-y-1">
                          {info.characteristics.map((char, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <div className="w-1 h-1 bg-current rounded-full mt-2 flex-shrink-0" />
                              {char}
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="font-medium mb-2">Ideal for:</h4>
                        <ul className="text-sm text-muted-foreground space-y-1">
                          {info.idealFor.map((ideal, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <div className="w-1 h-1 bg-current rounded-full mt-2 flex-shrink-0" />
                              {ideal}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </RadioGroup>

      {/* Help Section */}
      <Card className="bg-amber-50 border-amber-200 dark:bg-amber-950 dark:border-amber-800">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <Info className="h-5 w-5 text-amber-600 mt-0.5" />
            <div className="space-y-2">
              <h4 className="font-medium text-amber-900 dark:text-amber-100">
                Not sure which position suits you?
              </h4>
              <p className="text-sm text-amber-700 dark:text-amber-200">
                Don&apos;t worry! Your preferred position helps us suggest appropriate games and partners. 
                You can always change this later in your profile settings, and you&apos;ll naturally discover 
                your preferred style as you play more games.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between items-center pt-6">
        <Button variant="outline" onClick={handleSkip}>
          Skip for Now
        </Button>
        <Button 
          onClick={handleNext}
          disabled={!canProceed}
          size="lg"
        >
          Continue
        </Button>
      </div>
    </div>
  );
}