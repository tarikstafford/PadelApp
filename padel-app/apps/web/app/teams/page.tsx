'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Button } from '@workspace/ui/components/button';
import { Badge } from '@workspace/ui/components/badge';
import { Users, Plus, Trophy, Calendar } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';

interface Team {
  id: number;
  name: string;
  players: Array<{
    id: number;
    full_name: string;
    elo_rating: number;
  }>;
}

export default function TeamsPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/auth/login');
    } else if (user) {
      fetchTeams();
    }
  }, [user, authLoading, router]);

  const fetchTeams = async () => {
    try {
      const data = await apiClient.get<Team[]>('/users/me/teams');
      setTeams(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch teams');
    } finally {
      setLoading(false);
    }
  };

  const calculateAverageElo = (team: Team) => {
    if (team.players.length === 0) return 0;
    const totalElo = team.players.reduce((sum, player) => sum + player.elo_rating, 0);
    return Math.round(totalElo / team.players.length);
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen bg-background py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-muted rounded w-1/3 mb-4"></div>
            <div className="h-4 bg-muted rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-muted rounded w-1/3 mb-4"></div>
            <div className="h-4 bg-muted rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">My Teams</h1>
              <p className="text-muted-foreground">Manage your teams and register for tournaments</p>
            </div>
            <Link href="/teams/create">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Team
              </Button>
            </Link>
          </div>
        </div>

        {error && (
          <Card className="mb-6">
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
                <Button onClick={fetchTeams}>Retry</Button>
              </div>
            </CardContent>
          </Card>
        )}

        {teams.length === 0 && !error ? (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-12">
                <Users className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">No teams yet</h3>
                <p className="text-muted-foreground mb-6">
                  Create your first team to start participating in tournaments and competing with other players.
                </p>
                <Link href="/teams/create">
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Your First Team
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {teams.map((team) => (
              <Card key={team.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{team.name}</CardTitle>
                      <CardDescription>{team.players.length} members</CardDescription>
                    </div>
                    <Badge variant="outline">
                      Avg ELO: {calculateAverageElo(team)}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-sm text-foreground mb-2">Team Members</h4>
                      <div className="space-y-1">
                        {team.players.map((player) => (
                          <div key={player.id} className="flex justify-between text-sm">
                            <span className="text-foreground">{player.full_name}</span>
                            <span className="text-muted-foreground">ELO: {player.elo_rating}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="pt-4 space-y-2">
                      <Link href={`/teams/${team.id}`} className="w-full">
                        <Button className="w-full" variant="default">
                          <Users className="h-4 w-4 mr-2" />
                          View Team Details
                        </Button>
                      </Link>
                      <Link href="/tournaments" className="w-full">
                        <Button className="w-full" variant="outline">
                          <Trophy className="h-4 w-4 mr-2" />
                          Browse Tournaments
                        </Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Ready to compete?</CardTitle>
              <CardDescription>Browse available tournaments and register your teams</CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/tournaments">
                <Button>
                  <Calendar className="h-4 w-4 mr-2" />
                  View Tournaments
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}