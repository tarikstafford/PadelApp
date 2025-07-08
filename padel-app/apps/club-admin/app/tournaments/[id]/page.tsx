'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowLeft, Settings, Trophy, Calendar, Users, DollarSign } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';

interface Tournament {
  id: number;
  name: string;
  description: string;
  tournament_type: string;
  start_date: string;
  end_date: string;
  registration_deadline: string;
  status: string;
  max_participants: number;
  entry_fee: number;
  total_registered_teams: number;
  categories: Category[];
}

interface Category {
  id: number;
  category: string;
  max_participants: number;
  min_elo: number;
  max_elo: number;
  current_participants: number;
}

interface Team {
  id: number;
  team_id: number;
  team_name: string;
  category: string;
  seed: number;
  average_elo: number;
  registration_date: string;
  players: Array<{
    id: number;
    name: string;
    elo: number;
  }>;
}

interface Match {
  id: number;
  category: string;
  team1_name: string;
  team2_name: string;
  round_number: number;
  match_number: number;
  scheduled_time: string;
  court_name: string;
  status: string;
  team1_score: number;
  team2_score: number;
  winning_team_id: number;
}

const statusColors = {
  DRAFT: 'bg-gray-500',
  REGISTRATION_OPEN: 'bg-green-500',
  REGISTRATION_CLOSED: 'bg-yellow-500',
  IN_PROGRESS: 'bg-blue-500',
  COMPLETED: 'bg-purple-500',
  CANCELLED: 'bg-red-500'
};

export default function TournamentDetailsPage() {
  const params = useParams();
  const tournamentId = params.id as string;
  
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [teams, setTeams] = useState<Team[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTournamentData = useCallback(async () => {
    try {
      // Fetch tournament details
      const tournamentData = await apiClient.get<Tournament>(`/tournaments/${tournamentId}`);
      setTournament(tournamentData);

      // Fetch teams (optional, don't fail if it doesn't exist)
      try {
        const teamsData = await apiClient.get<Team[]>(`/tournaments/${tournamentId}/teams`);
        setTeams(teamsData);
      } catch (error) {
        console.log('Teams endpoint not available:', error);
        setTeams([]);
      }

      // Fetch matches (optional, don't fail if it doesn't exist)
      try {
        const matchesData = await apiClient.get<Match[]>(`/tournaments/${tournamentId}/matches`);
        setMatches(matchesData);
      } catch (error) {
        console.log('Matches endpoint not available:', error);
        setMatches([]);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [tournamentId]);

  useEffect(() => {
    if (tournamentId) {
      fetchTournamentData();
    }
  }, [tournamentId, fetchTournamentData]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatTournamentType = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getStatusLabel = (status: string) => {
    return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const groupTeamsByCategory = (teams: Team[]) => {
    return teams.reduce((acc, team) => {
      if (!acc[team.category]) {
        acc[team.category] = [];
      }
      acc[team.category]!.push(team);
      return acc;
    }, {} as Record<string, Team[]>);
  };

  const groupMatchesByCategory = (matches: Match[]) => {
    return matches.reduce((acc, match) => {
      if (!acc[match.category]) {
        acc[match.category] = [];
      }
      acc[match.category]!.push(match);
      return acc;
    }, {} as Record<string, Match[]>);
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (error || !tournament) {
    return (
      <div className="space-y-6">
        <Link href="/tournaments">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Tournaments
          </Button>
        </Link>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-red-600 mb-4">{error || 'Tournament not found'}</p>
              <Button onClick={fetchTournamentData}>Retry</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/tournaments">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Tournaments
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">{tournament.name}</h1>
            <p className="text-gray-600">{formatTournamentType(tournament.tournament_type)}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge className={`${statusColors[tournament.status as keyof typeof statusColors]} text-white`}>
            {getStatusLabel(tournament.status)}
          </Badge>
          <Link href={`/tournaments/${tournament.id}/manage`}>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Manage
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Teams</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {tournament.total_registered_teams} / {tournament.max_participants}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Entry Fee</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${tournament.entry_fee}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Start Date</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-sm">{formatDate(tournament.start_date)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">End Date</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-sm">{formatDate(tournament.end_date)}</div>
          </CardContent>
        </Card>
      </div>

      {tournament.description && (
        <Card>
          <CardHeader>
            <CardTitle>Description</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700">{tournament.description}</p>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="teams" className="space-y-6">
        <TabsList>
          <TabsTrigger value="teams">Teams</TabsTrigger>
          <TabsTrigger value="matches">Matches</TabsTrigger>
          <TabsTrigger value="bracket">Bracket</TabsTrigger>
        </TabsList>

        <TabsContent value="teams" className="space-y-6">
          {Object.entries(groupTeamsByCategory(teams)).map(([category, categoryTeams]) => (
            <Card key={category}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {category} Category
                  <Badge variant="outline">{categoryTeams.length} teams</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {categoryTeams.map((team) => (
                    <div key={team.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h4 className="font-medium">{team.team_name}</h4>
                        <p className="text-sm text-gray-600">
                          Seed: #{team.seed} | Avg ELO: {team.average_elo.toFixed(2)}
                        </p>
                        <div className="flex gap-2 mt-1">
                          {team.players.map((player) => (
                            <span key={player.id} className="text-xs bg-gray-100 px-2 py-1 rounded">
                              {player.name} ({player.elo.toFixed(1)})
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="text-sm text-gray-500">
                        Registered: {formatDate(team.registration_date)}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="matches" className="space-y-6">
          {Object.entries(groupMatchesByCategory(matches)).map(([category, categoryMatches]) => (
            <Card key={category}>
              <CardHeader>
                <CardTitle>{category} Category Matches</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {categoryMatches.map((match) => (
                    <div key={match.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h4 className="font-medium">
                          Round {match.round_number}, Match {match.match_number}
                        </h4>
                        <p className="text-sm">
                          {match.team1_name} vs {match.team2_name}
                        </p>
                        {match.scheduled_time && (
                          <p className="text-xs text-gray-600">
                            {formatDate(match.scheduled_time)} | {match.court_name}
                          </p>
                        )}
                      </div>
                      <div className="text-right">
                        <Badge 
                          variant={match.status === 'COMPLETED' ? 'default' : 'outline'}
                        >
                          {match.status}
                        </Badge>
                        {match.status === 'COMPLETED' && (
                          <p className="text-sm mt-1">
                            {match.team1_score} - {match.team2_score}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="bracket">
          <Card>
            <CardHeader>
              <CardTitle>Tournament Bracket</CardTitle>
              <CardDescription>Visual representation of tournament progress</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <Trophy className="mx-auto h-12 w-12 mb-4" />
                <p>Bracket visualization will be implemented here</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}