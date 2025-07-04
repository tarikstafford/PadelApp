"use client";

import { useEffect, useState } from 'react';
import { Trophy, Users, Calendar, DollarSign, Plus } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useClub } from '@/contexts/ClubContext';
import { apiClient } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface TournamentSummary {
  id: number;
  name: string;
  status: string;
  participants: number;
  max_participants: number;
  start_date: string;
  end_date: string;
  entry_fee: number;
}

export function TournamentStatusWidget() {
  const router = useRouter();
  const { selectedClub } = useClub();
  const [tournaments, setTournaments] = useState<TournamentSummary[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchActiveTournaments = async () => {
    if (!selectedClub) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<TournamentSummary[]>(`/business/club/${selectedClub.id}/tournaments/active`);
      setTournaments(response);
    } catch (err) {
      console.error('Failed to fetch active tournaments:', err);
      setError('Failed to load tournaments');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchActiveTournaments();
  }, [selectedClub]);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'registration_open':
        return 'bg-green-100 text-green-800';
      case 'registration_closed':
        return 'bg-blue-100 text-blue-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-gray-100 text-gray-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status.toLowerCase()) {
      case 'registration_open':
        return 'Open';
      case 'registration_closed':
        return 'Closed';
      case 'in_progress':
        return 'Active';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
    }).format(amount);
  };

  const handleCreateTournament = () => {
    router.push('/tournaments/new');
  };

  const handleViewTournament = (tournamentId: number) => {
    router.push(`/tournaments/${tournamentId}`);
  };

  const handleViewAllTournaments = () => {
    router.push('/tournaments');
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Active Tournaments</CardTitle>
            <CardDescription>
              {tournaments.length} tournaments currently running
            </CardDescription>
          </div>
          <Button onClick={handleCreateTournament} size="sm">
            <Plus className="h-4 w-4 mr-1" />
            New Tournament
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="p-3 border rounded-lg">
                <div className="h-4 w-32 bg-gray-200 animate-pulse rounded mb-2" />
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <div className="h-3 w-20 bg-gray-200 animate-pulse rounded" />
                    <div className="h-3 w-16 bg-gray-200 animate-pulse rounded" />
                  </div>
                  <div className="h-6 w-16 bg-gray-200 animate-pulse rounded" />
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-8 text-gray-500">
            <p>{error}</p>
            <Button variant="outline" onClick={fetchActiveTournaments} className="mt-2">
              Try Again
            </Button>
          </div>
        ) : tournaments.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Trophy className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No active tournaments</p>
            <p className="text-sm mb-4">Create your first tournament to get started</p>
            <Button onClick={handleCreateTournament} variant="outline">
              <Plus className="h-4 w-4 mr-1" />
              Create Tournament
            </Button>
          </div>
        ) : (
          <>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {tournaments.map((tournament) => (
                <div
                  key={tournament.id}
                  className="p-3 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => handleViewTournament(tournament.id)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-sm line-clamp-1">{tournament.name}</h4>
                    <Badge className={getStatusColor(tournament.status)} variant="secondary">
                      {getStatusLabel(tournament.status)}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-1">
                        <Users className="h-3 w-3" />
                        <span>
                          {tournament.participants}/{tournament.max_participants} players
                        </span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Calendar className="h-3 w-3" />
                        <span>
                          {formatDate(tournament.start_date)} - {formatDate(tournament.end_date)}
                        </span>
                      </div>
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center space-x-1">
                        <DollarSign className="h-3 w-3" />
                        <span>
                          {tournament.entry_fee > 0 
                            ? formatCurrency(tournament.entry_fee)
                            : 'Free'
                          }
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="text-blue-600 hover:text-blue-800">
                          View details →
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Progress bar for participants */}
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-1">
                      <div
                        className="bg-blue-600 h-1 rounded-full transition-all duration-300"
                        style={{
                          width: `${Math.min(
                            (tournament.participants / tournament.max_participants) * 100,
                            100
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {tournaments.length > 0 && (
              <div className="mt-4 pt-4 border-t">
                <Button 
                  variant="outline" 
                  onClick={handleViewAllTournaments}
                  className="w-full"
                >
                  View All Tournaments
                </Button>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}