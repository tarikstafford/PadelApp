'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Trophy, Medal, Award, Crown } from 'lucide-react';

interface TournamentTrophy {
  id: number;
  tournament_id: number;
  tournament_name: string;
  category: string;
  position: number;
  trophy_type: string;
  awarded_at: string;
}

const TROPHY_ICONS = {
  WINNER: Crown,
  RUNNER_UP: Trophy,
  SEMI_FINALIST: Medal,
  PARTICIPANT: Award,
};

const TROPHY_COLORS = {
  WINNER: 'text-yellow-500',
  RUNNER_UP: 'text-gray-400',
  SEMI_FINALIST: 'text-amber-600',
  PARTICIPANT: 'text-blue-500',
};

const CATEGORY_COLORS = {
  BRONZE: 'bg-amber-100 text-amber-800',
  SILVER: 'bg-gray-100 text-gray-800',
  GOLD: 'bg-yellow-100 text-yellow-800',
  PLATINUM: 'bg-purple-100 text-purple-800',
};

export default function TrophyDisplay({ userId }: { userId: number }) {
  const [trophies, setTrophies] = useState<TournamentTrophy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTrophies = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1/users/${userId}/trophies`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTrophies(data);
      } else {
        throw new Error('Failed to fetch trophies');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchTrophies();
  }, [fetchTrophies]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getPositionText = (position: number) => {
    switch (position) {
      case 1:
        return '1st Place';
      case 2:
        return '2nd Place';
      case 3:
        return '3rd Place';
      default:
        return `${position}th Place`;
    }
  };

  const groupTrophiesByType = (trophies: TournamentTrophy[]) => {
    return trophies.reduce((acc, trophy) => {
      if (!acc[trophy.trophy_type]) {
        acc[trophy.trophy_type] = [];
      }
      acc[trophy.trophy_type]!.push(trophy);
      return acc;
    }, {} as Record<string, TournamentTrophy[]>);
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5" />
            Trophy Cabinet
          </CardTitle>
          <CardDescription>Your tournament achievements</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5" />
            Trophy Cabinet
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-600 text-sm">{error}</p>
        </CardContent>
      </Card>
    );
  }

  if (trophies.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5" />
            Trophy Cabinet
          </CardTitle>
          <CardDescription>Your tournament achievements</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Trophy className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-600">No trophies yet</p>
            <p className="text-sm text-gray-500">Participate in tournaments to earn your first trophy!</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const groupedTrophies = groupTrophiesByType(trophies);
  const trophyStats = {
    total: trophies.length,
    winners: trophies.filter(t => t.trophy_type === 'WINNER').length,
    runnerUps: trophies.filter(t => t.trophy_type === 'RUNNER_UP').length,
    categories: [...new Set(trophies.map(t => t.category))].length,
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Trophy className="h-5 w-5" />
          Trophy Cabinet
        </CardTitle>
        <CardDescription>Your tournament achievements</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Trophy Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{trophyStats.total}</div>
            <div className="text-sm text-gray-600">Total Trophies</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">{trophyStats.winners}</div>
            <div className="text-sm text-gray-600">Championships</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-600">{trophyStats.runnerUps}</div>
            <div className="text-sm text-gray-600">Runner-ups</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{trophyStats.categories}</div>
            <div className="text-sm text-gray-600">Categories</div>
          </div>
        </div>

        {/* Trophy List by Type */}
        <div className="space-y-6">
          {Object.entries(groupedTrophies).map(([trophyType, typeTrophies]) => {
            const IconComponent = TROPHY_ICONS[trophyType as keyof typeof TROPHY_ICONS] || Award;
            const iconColor = TROPHY_COLORS[trophyType as keyof typeof TROPHY_COLORS] || 'text-gray-500';
            
            return (
              <div key={trophyType}>
                <h4 className="flex items-center gap-2 font-medium mb-3">
                  <IconComponent className={`h-5 w-5 ${iconColor}`} />
                  {trophyType.replace('_', ' ')} ({typeTrophies.length})
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {typeTrophies.map((trophy) => (
                    <div key={trophy.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h5 className="font-medium text-sm line-clamp-2">{trophy.tournament_name}</h5>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge 
                              variant="outline" 
                              className={`text-xs ${CATEGORY_COLORS[trophy.category as keyof typeof CATEGORY_COLORS] || 'bg-gray-100 text-gray-800'}`}
                            >
                              {trophy.category}
                            </Badge>
                            {trophy.position && (
                              <span className="text-xs text-gray-600">
                                {getPositionText(trophy.position)}
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {formatDate(trophy.awarded_at)}
                          </p>
                        </div>
                        <IconComponent className={`h-6 w-6 ${iconColor} flex-shrink-0`} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}