'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Plus, Calendar, Users, Trophy, Settings, Tag } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import { CategoryBadgeGrid } from '@/components/tournaments/CategoryBadge';
import { TournamentCategory } from '@/lib/types';

interface Tournament {
  id: number;
  name: string;
  tournament_type: string;
  start_date: string;
  end_date: string;
  status: string;
  total_registered_teams: number;
  max_participants: number;
  categories?: {
    id: number;
    category: TournamentCategory;
    max_participants: number;
    min_elo: number;
    max_elo: number;
    current_participants: number;
    current_teams: number;
    current_individuals: number;
  }[];
}

// Helper function to convert API response to typed Tournament
function convertApiTournament(apiTournament: Record<string, unknown>): Tournament {
  return {
    ...apiTournament,
    categories: (apiTournament.categories as Array<Record<string, unknown>>)?.map((cat: Record<string, unknown>) => ({
      id: cat.id as number,
      category: cat.category as TournamentCategory,
      max_participants: cat.max_participants as number,
      min_elo: cat.min_elo as number,
      max_elo: cat.max_elo as number,
      current_participants: cat.current_participants as number,
      current_teams: cat.current_teams as number,
      current_individuals: cat.current_individuals as number,
    }))
  } as Tournament;
}

const statusColors = {
  DRAFT: 'bg-gray-500',
  REGISTRATION_OPEN: 'bg-green-500',
  REGISTRATION_CLOSED: 'bg-yellow-500',
  IN_PROGRESS: 'bg-blue-500',
  COMPLETED: 'bg-purple-500',
  CANCELLED: 'bg-red-500'
};

const statusLabels = {
  DRAFT: 'Draft',
  REGISTRATION_OPEN: 'Registration Open',
  REGISTRATION_CLOSED: 'Registration Closed',
  IN_PROGRESS: 'In Progress',
  COMPLETED: 'Completed',
  CANCELLED: 'Cancelled'
};

export default function TournamentsPage() {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTournaments();
  }, []);

  const fetchTournaments = async () => {
    try {
      const data = await apiClient.get<Array<Record<string, unknown>>>('/tournaments/club');
      const convertedTournaments = data.map(convertApiTournament);
      setTournaments(convertedTournaments);
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err && (err as { response?: { status?: number } }).response?.status === 404) {
        // 404 means no tournaments found - show empty state
        setTournaments([]);
      } else {
        setError(err instanceof Error ? err.message : 'An error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatTournamentType = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Tournaments</h1>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="h-3 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Tournaments</h1>
        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-red-600 mb-4">{error}</p>
              <Button onClick={fetchTournaments}>Retry</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Tournaments</h1>
        <Link href="/tournaments/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Tournament
          </Button>
        </Link>
      </div>

      {tournaments.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-8">
              <Trophy className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No tournaments yet</h3>
              <p className="text-gray-600 mb-4">
                Create your first tournament to start organizing competitive play at your club.
              </p>
              <Link href="/tournaments/new">
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Your First Tournament
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tournaments.map((tournament) => (
            <Card key={tournament.id} className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">{tournament.name}</CardTitle>
                    <CardDescription>{formatTournamentType(tournament.tournament_type)}</CardDescription>
                  </div>
                  <Badge 
                    className={`${statusColors[tournament.status as keyof typeof statusColors]} text-white`}
                  >
                    {statusLabels[tournament.status as keyof typeof statusLabels]}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center text-sm text-gray-600">
                    <Calendar className="mr-2 h-4 w-4" />
                    {formatDate(tournament.start_date)} - {formatDate(tournament.end_date)}
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <Users className="mr-2 h-4 w-4" />
                    {tournament.total_registered_teams} / {tournament.max_participants} teams
                  </div>
                  
                  {tournament.categories && tournament.categories.length > 0 && (
                    <div className="space-y-2">
                      <div className="flex items-center text-sm text-gray-600">
                        <Tag className="mr-2 h-4 w-4" />
                        Categories
                      </div>
                      <CategoryBadgeGrid
                        categories={tournament.categories}
                        size="sm"
                        showParticipantCount={true}
                      />
                    </div>
                  )}
                  
                  <div className="flex gap-2 pt-2">
                    <Link href={`/tournaments/${tournament.id}`} className="flex-1">
                      <Button variant="outline" size="sm" className="w-full">
                        View Details
                      </Button>
                    </Link>
                    <Link href={`/tournaments/${tournament.id}/manage`}>
                      <Button variant="outline" size="sm">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}