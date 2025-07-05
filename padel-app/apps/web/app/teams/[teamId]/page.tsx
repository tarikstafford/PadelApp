"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Button } from '@workspace/ui/components/button';
import { Badge } from '@workspace/ui/components/badge';
import { Separator } from '@workspace/ui/components/separator';
import { Avatar, AvatarFallback, AvatarImage } from '@workspace/ui/components/avatar';
import { 
  ArrowLeft, 
  Users, 
  Trophy, 
 
  Calendar,
  UserPlus,
  UserMinus,
  Settings,
  BarChart3,
  Target,
  Flame,
  Crown
} from 'lucide-react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import { format } from 'date-fns';
import withAuth from '@/components/auth/withAuth';

interface TeamMember {
  id: number;
  full_name: string;
  email: string;
  elo_rating: number;
  profile_picture_url?: string;
}

interface TeamStats {
  id: number;
  team_id: number;
  games_played: number;
  games_won: number;
  games_lost: number;
  total_points_scored: number;
  total_points_conceded: number;
  current_average_elo: number;
  peak_average_elo: number;
  lowest_average_elo: number;
  tournaments_participated: number;
  tournaments_won: number;
  current_win_streak: number;
  current_loss_streak: number;
  longest_win_streak: number;
  longest_loss_streak: number;
  last_game_date?: string;
  last_updated: string;
  created_at: string;
}

interface TeamGameHistory {
  id: number;
  team_id: number;
  game_id: number;
  won: number;
  points_scored: number;
  points_conceded: number;
  opponent_team_id?: number;
  elo_before?: number;
  elo_after?: number;
  elo_change?: number;
  game_date: string;
  is_tournament_game: number;
  tournament_id?: number;
  created_at: string;
  game?: {
    id: number;
    club?: {
      name: string;
      city: string;
    };
  };
  opponent_team?: {
    id: number;
    name: string;
  };
  tournament?: {
    id: number;
    name: string;
  };
}

interface TeamDetail {
  id: number;
  name: string;
  players: TeamMember[];
  stats?: TeamStats;
  recent_games?: TeamGameHistory[];
}

function TeamDetailPage() {
  const params = useParams();
  const { accessToken } = useAuth();
  const [team, setTeam] = useState<TeamDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const teamId = params.teamId as string;

  const fetchTeamDetail = useCallback(async () => {
    if (!accessToken || !teamId) return;

    setIsLoading(true);
    try {
      // Note: This endpoint would need to be created in the backend
      const response = await apiClient.get<TeamDetail>(`/teams/${teamId}`, undefined, accessToken);
      setTeam(response);
    } catch (error: unknown) {
      console.error('Error fetching team details:', error);
      setError((error as any).response?.data?.detail || 'Failed to load team details');
    } finally {
      setIsLoading(false);
    }
  }, [teamId, accessToken]);

  useEffect(() => {
    fetchTeamDetail();
  }, [fetchTeamDetail]);

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto py-8 px-4 space-y-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-1/3"></div>
          <div className="h-4 bg-muted rounded w-1/2"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-40 bg-muted rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error || !team) {
    return (
      <div className="max-w-6xl mx-auto py-8 px-4">
        <div className="flex items-center space-x-4 mb-6">
          <Link href="/teams">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Teams
            </Button>
          </Link>
        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-8">
              <p className="text-destructive mb-4">{error || 'Team not found'}</p>
              <Button onClick={fetchTeamDetail}>Try Again</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const calculateAverageElo = () => {
    if (team.players.length === 0) return 0;
    const totalElo = team.players.reduce((sum, player) => sum + player.elo_rating, 0);
    return Math.round(totalElo / team.players.length);
  };

  const calculateWinRate = () => {
    if (!team.stats || team.stats.games_played === 0) return 0;
    return Math.round((team.stats.games_won / team.stats.games_played) * 100);
  };

  const stats = team.stats;

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/teams">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Teams
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{team.name}</h1>
            <p className="text-muted-foreground">
              {team.players.length} member{team.players.length !== 1 ? 's' : ''} • Avg ELO: {calculateAverageElo()}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <UserPlus className="h-4 w-4 mr-2" />
            Add Player
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <BarChart3 className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">Games Played</p>
                  <p className="text-2xl font-bold">{stats.games_played}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Trophy className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">Win Rate</p>
                  <p className="text-2xl font-bold">{calculateWinRate()}%</p>
                  <p className="text-xs text-muted-foreground">{stats.games_won} wins</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Target className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">Avg ELO</p>
                  <p className="text-2xl font-bold">{Math.round(stats.current_average_elo || calculateAverageElo())}</p>
                  <p className="text-xs text-muted-foreground">
                    Peak: {Math.round(stats.peak_average_elo || 0)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Flame className="h-8 w-8 text-orange-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">Current Streak</p>
                  <p className="text-2xl font-bold">
                    {stats.current_win_streak > 0 ? stats.current_win_streak : stats.current_loss_streak}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {stats.current_win_streak > 0 ? 'win streak' : 'loss streak'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Team Members */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="mr-2 h-5 w-5" />
                Team Members
              </CardTitle>
              <CardDescription>
                Manage your team roster and player details
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {team.players.map((player) => (
                  <div key={player.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <Avatar className="h-10 w-10">
                        <AvatarImage src={player.profile_picture_url} alt={player.full_name} />
                        <AvatarFallback>{player.full_name.charAt(0)}</AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium">{player.full_name}</p>
                        <p className="text-sm text-muted-foreground">{player.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">ELO: {player.elo_rating}</Badge>
                      <Button variant="ghost" size="sm">
                        <UserMinus className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Performance Details */}
        <div className="space-y-6">
          {stats && (
            <>
              {/* Performance Stats */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BarChart3 className="mr-2 h-5 w-5" />
                    Performance
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Points Scored</span>
                      <span className="font-medium">{stats.total_points_scored}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Points Conceded</span>
                      <span className="font-medium">{stats.total_points_conceded}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Point Differential</span>
                      <span className={`font-medium ${stats.total_points_scored - stats.total_points_conceded >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {stats.total_points_scored - stats.total_points_conceded > 0 ? '+' : ''}
                        {stats.total_points_scored - stats.total_points_conceded}
                      </span>
                    </div>
                  </div>

                  <Separator />

                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Longest Win Streak</span>
                      <span className="font-medium">{stats.longest_win_streak}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">ELO Range</span>
                      <span className="font-medium text-xs">
                        {Math.round(stats.lowest_average_elo || 0)} - {Math.round(stats.peak_average_elo || 0)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Tournament Stats */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Crown className="mr-2 h-5 w-5" />
                    Tournaments
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Participated</span>
                      <span className="font-medium">{stats.tournaments_participated}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Won</span>
                      <span className="font-medium">{stats.tournaments_won}</span>
                    </div>
                    {stats.tournaments_participated > 0 && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Win Rate</span>
                        <span className="font-medium">
                          {Math.round((stats.tournaments_won / stats.tournaments_participated) * 100)}%
                        </span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </>
          )}

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Link href="/tournaments" className="w-full">
                <Button variant="outline" className="w-full">
                  <Trophy className="h-4 w-4 mr-2" />
                  Browse Tournaments
                </Button>
              </Link>
              <Button variant="outline" className="w-full">
                <Calendar className="h-4 w-4 mr-2" />
                Schedule Practice
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Recent Games */}
      {team.recent_games && team.recent_games.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calendar className="mr-2 h-5 w-5" />
              Recent Games
            </CardTitle>
            <CardDescription>
              Your team&apos;s recent game history and performance
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {team.recent_games.slice(0, 5).map((game) => (
                <div key={game.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className={`w-3 h-3 rounded-full ${game.won ? 'bg-green-500' : 'bg-red-500'}`} />
                    <div>
                      <p className="font-medium">
                        vs {game.opponent_team?.name || 'Unknown Team'}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {format(new Date(game.game_date), 'MMM d, yyyy')}
                        {game.game?.club && ` • ${game.game.club.name}`}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">
                      {game.points_scored} - {game.points_conceded}
                    </p>
                    {game.elo_change && (
                      <p className={`text-sm ${game.elo_change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {game.elo_change > 0 ? '+' : ''}{Math.round(game.elo_change)} ELO
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default withAuth(TeamDetailPage);