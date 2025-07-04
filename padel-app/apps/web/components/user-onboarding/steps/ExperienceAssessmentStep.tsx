"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Button } from '@workspace/ui/components/button';
import { Input } from '@workspace/ui/components/input';
import { Label } from '@workspace/ui/components/label';
import { Checkbox } from '@workspace/ui/components/checkbox';
import { RadioGroup, RadioGroupItem } from '@workspace/ui/components/radio-group';
import { Separator } from '@workspace/ui/components/separator';
import { useUserOnboarding } from '../UserOnboardingProvider';
import { ExperienceAssessment, PlayingFrequency, SkillLevel } from '../types';
import { HelpCircle, Trophy, Calendar, Users, Target } from 'lucide-react';
import { cn } from '@/lib/utils';

const SPORT_OPTIONS = [
  'Tennis',
  'Squash',
  'Badminton',
  'Ping Pong',
  'Pickleball',
  'Other racquet sport'
];

const FREQUENCY_OPTIONS: { value: PlayingFrequency; label: string; description: string }[] = [
  { value: 'rarely', label: 'Rarely', description: 'A few times a year' },
  { value: 'monthly', label: 'Monthly', description: '1-3 times per month' },
  { value: 'weekly', label: 'Weekly', description: '1-3 times per week' },
  { value: 'daily', label: 'Daily', description: 'Almost every day' }
];

const SKILL_LEVELS: { value: SkillLevel; label: string; description: string }[] = [
  { value: 1, label: 'Complete Beginner', description: 'Never played padel before' },
  { value: 2, label: 'Beginner', description: 'Played a few times, learning basics' },
  { value: 3, label: 'Recreational', description: 'Play occasionally, comfortable with basics' },
  { value: 4, label: 'Intermediate', description: 'Regular player with good technique' },
  { value: 5, label: 'Advanced', description: 'Competitive player with strong skills' }
];

export function ExperienceAssessmentStep() {
  const { userData, updateExperienceData, nextStep, setError } = useUserOnboarding();
  const [localData, setLocalData] = useState<Partial<ExperienceAssessment>>(userData.experienceData);
  const [canProceed, setCanProceed] = useState(false);

  // Validate form completion
  useEffect(() => {
    const isValid = 
      localData.yearsPlaying !== undefined &&
      localData.selfAssessedSkill !== undefined &&
      localData.playingFrequency !== undefined;
    
    setCanProceed(isValid);
  }, [localData]);

  const handleYearsChange = (value: string) => {
    const years = Math.max(0, Math.min(50, parseInt(value) || 0));
    const newData = { ...localData, yearsPlaying: years };
    setLocalData(newData);
    updateExperienceData(newData);
  };

  const handleSportToggle = (sport: string, checked: boolean) => {
    const currentSports = localData.previousSports || [];
    const newSports = checked 
      ? [...currentSports, sport]
      : currentSports.filter(s => s !== sport);
    
    const newData = { ...localData, previousSports: newSports };
    setLocalData(newData);
    updateExperienceData(newData);
  };

  const handleSkillLevelChange = (value: string) => {
    const skill = parseInt(value) as SkillLevel;
    const newData = { ...localData, selfAssessedSkill: skill };
    setLocalData(newData);
    updateExperienceData(newData);
  };

  const handleFrequencyChange = (value: string) => {
    const frequency = value as PlayingFrequency;
    const newData = { ...localData, playingFrequency: frequency };
    setLocalData(newData);
    updateExperienceData(newData);
  };

  const handleBooleanChange = (field: keyof ExperienceAssessment, value: boolean) => {
    const newData = { ...localData, [field]: value };
    setLocalData(newData);
    updateExperienceData(newData);
  };

  const handleNext = () => {
    if (!canProceed) {
      setError('Please complete all required fields before continuing.');
      return;
    }
    
    setError(null);
    nextStep();
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Tell Us About Your Experience</h1>
        <p className="text-muted-foreground">
          Help us understand your padel background so we can provide the best experience for you.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Playing History
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Years Playing */}
          <div className="space-y-2">
            <Label htmlFor="years-playing">
              How many years have you been playing padel? *
            </Label>
            <Input
              id="years-playing"
              type="number"
              min="0"
              max="50"
              value={localData.yearsPlaying || ''}
              onChange={(e) => handleYearsChange(e.target.value)}
              placeholder="Enter number of years"
              className="max-w-xs"
            />
            <p className="text-xs text-muted-foreground">
              Enter 0 if you are completely new to padel
            </p>
          </div>

          {/* Previous Sports */}
          <div className="space-y-3">
            <Label>Previous racquet sport experience (select all that apply)</Label>
            <div className="grid grid-cols-2 gap-3">
              {SPORT_OPTIONS.map((sport) => (
                <div key={sport} className="flex items-center space-x-2">
                  <Checkbox
                    id={`sport-${sport}`}
                    checked={(localData.previousSports || []).includes(sport)}
                    onCheckedChange={(checked) => handleSportToggle(sport, checked as boolean)}
                  />
                  <Label htmlFor={`sport-${sport}`} className="text-sm">
                    {sport}
                  </Label>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Current Skill Level
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Self Assessment */}
          <div className="space-y-4">
            <Label>How would you rate your current padel skill level? *</Label>
            <RadioGroup
              value={localData.selfAssessedSkill?.toString()}
              onValueChange={handleSkillLevelChange}
              className="space-y-3"
            >
              {SKILL_LEVELS.map((level) => (
                <div key={level.value} className="flex items-start space-x-3">
                  <RadioGroupItem
                    value={level.value.toString()}
                    id={`skill-${level.value}`}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <Label htmlFor={`skill-${level.value}`} className="font-medium">
                      {level.label}
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      {level.description}
                    </p>
                  </div>
                </div>
              ))}
            </RadioGroup>
          </div>

          {/* Playing Frequency */}
          <div className="space-y-4">
            <Label>How often do you typically play padel? *</Label>
            <RadioGroup
              value={localData.playingFrequency}
              onValueChange={handleFrequencyChange}
              className="grid grid-cols-2 gap-4"
            >
              {FREQUENCY_OPTIONS.map((option) => (
                <div key={option.value} className="flex items-start space-x-3">
                  <RadioGroupItem
                    value={option.value}
                    id={`frequency-${option.value}`}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <Label htmlFor={`frequency-${option.value}`} className="font-medium">
                      {option.label}
                    </Label>
                    <p className="text-xs text-muted-foreground">
                      {option.description}
                    </p>
                  </div>
                </div>
              ))}
            </RadioGroup>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5" />
            Competitive Experience
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Competitive Experience */}
          <div className="flex items-start space-x-3">
            <Checkbox
              id="competitive"
              checked={localData.competitiveExperience || false}
              onCheckedChange={(checked) => handleBooleanChange('competitiveExperience', checked as boolean)}
            />
            <div className="flex-1">
              <Label htmlFor="competitive" className="font-medium">
                I have competitive playing experience
              </Label>
              <p className="text-sm text-muted-foreground">
                Played in leagues, clubs, or regular competitive matches
              </p>
            </div>
          </div>

          {/* Tournament Participation */}
          <div className="flex items-start space-x-3">
            <Checkbox
              id="tournaments"
              checked={localData.tournamentParticipation || false}
              onCheckedChange={(checked) => handleBooleanChange('tournamentParticipation', checked as boolean)}
            />
            <div className="flex-1">
              <Label htmlFor="tournaments" className="font-medium">
                I have participated in tournaments
              </Label>
              <p className="text-sm text-muted-foreground">
                Formal tournament or championship experience
              </p>
            </div>
          </div>

          {/* Coaching Experience */}
          <div className="flex items-start space-x-3">
            <Checkbox
              id="coaching"
              checked={localData.coachingExperience || false}
              onCheckedChange={(checked) => handleBooleanChange('coachingExperience', checked as boolean)}
            />
            <div className="flex-1">
              <Label htmlFor="coaching" className="font-medium">
                I have coaching or teaching experience
              </Label>
              <p className="text-sm text-muted-foreground">
                Experience coaching padel or other racquet sports
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Help Section */}
      <Card className="bg-blue-50 border-blue-200 dark:bg-blue-950 dark:border-blue-800">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <HelpCircle className="h-5 w-5 text-blue-600 mt-0.5" />
            <div className="space-y-2">
              <h4 className="font-medium text-blue-900 dark:text-blue-100">
                Why do we ask these questions?
              </h4>
              <p className="text-sm text-blue-700 dark:text-blue-200">
                This information helps us estimate your initial skill rating and match you with players of similar ability. 
                Your rating will automatically adjust as you play more games, ensuring fair and competitive matches.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between items-center pt-6">
        <p className="text-sm text-muted-foreground">
          * Required for rating calculation
        </p>
        <Button 
          onClick={handleNext}
          disabled={!canProceed}
          size="lg"
        >
          Calculate My Rating
        </Button>
      </div>
    </div>
  );
}