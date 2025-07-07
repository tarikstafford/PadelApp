'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Users, User, Trophy, Shuffle } from 'lucide-react';
import { TournamentType } from '@/lib/types';

interface TournamentTypeSelectorProps {
  value: TournamentType | '';
  onChange: (type: TournamentType) => void;
}

const TOURNAMENT_TYPE_INFO = {
  [TournamentType.SINGLE_ELIMINATION]: {
    label: 'Single Elimination',
    description: 'Teams are eliminated after one loss. Classic knockout format.',
    icon: Trophy,
    requiresTeams: true,
    teamSize: 2,
    features: ['Quick tournament format', 'Clear winner path', 'Ideal for smaller groups'],
  },
  [TournamentType.DOUBLE_ELIMINATION]: {
    label: 'Double Elimination',
    description: 'Teams get a second chance. Lose twice to be eliminated.',
    icon: Trophy,
    requiresTeams: true,
    teamSize: 2,
    features: ['More games per team', 'Fairer competition', 'Winners and losers brackets'],
  },
  [TournamentType.AMERICANO]: {
    label: 'Americano',
    description: 'Individual players sign up and are paired randomly each round.',
    icon: Shuffle,
    requiresTeams: false,
    teamSize: 1,
    features: ['Individual registration', 'Dynamic team pairing', 'Social format', 'Points-based ranking'],
  },
  [TournamentType.FIXED_AMERICANO]: {
    label: 'Fixed Americano',
    description: 'Similar to Americano but with pre-set team rotations.',
    icon: Shuffle,
    requiresTeams: false,
    teamSize: 1,
    features: ['Individual registration', 'Predetermined pairings', 'Balanced matchups', 'Points-based ranking'],
  },
};

export default function TournamentTypeSelector({ value, onChange }: TournamentTypeSelectorProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Tournament Format</CardTitle>
        <CardDescription>
          Choose the competition format for your tournament
        </CardDescription>
      </CardHeader>
      <CardContent>
        <RadioGroup value={value} onValueChange={(val) => onChange(val as TournamentType)}>
          <div className="space-y-4">
            {Object.entries(TOURNAMENT_TYPE_INFO).map(([type, info]) => {
              const Icon = info.icon;
              return (
                <div key={type} className="relative">
                  <RadioGroupItem
                    value={type}
                    id={type}
                    className="peer sr-only"
                  />
                  <Label
                    htmlFor={type}
                    className="flex flex-col gap-3 rounded-lg border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <Icon className="h-5 w-5" />
                        <div>
                          <p className="font-medium">{info.label}</p>
                          <p className="text-sm text-muted-foreground">
                            {info.description}
                          </p>
                        </div>
                      </div>
                      <Badge variant={info.requiresTeams ? 'default' : 'secondary'}>
                        {info.requiresTeams ? (
                          <>
                            <Users className="h-3 w-3 mr-1" />
                            Teams of {info.teamSize}
                          </>
                        ) : (
                          <>
                            <User className="h-3 w-3 mr-1" />
                            Individual
                          </>
                        )}
                      </Badge>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {info.features.map((feature, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {feature}
                        </Badge>
                      ))}
                    </div>
                  </Label>
                </div>
              );
            })}
          </div>
        </RadioGroup>
      </CardContent>
    </Card>
  );
}