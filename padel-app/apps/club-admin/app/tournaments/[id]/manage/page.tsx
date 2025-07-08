'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import { Tournament } from '@/lib/types';
import TournamentManagement from '@/components/tournaments/TournamentManagement';


export default function TournamentManagePage() {
  const params = useParams();
  const tournamentId = params.id as string;
  
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTournament = useCallback(async () => {
    try {
      const tournamentData = await apiClient.get<Tournament>(`/tournaments/${tournamentId}`);
      setTournament(tournamentData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [tournamentId]);

  useEffect(() => {
    if (tournamentId) {
      fetchTournament();
    }
  }, [tournamentId, fetchTournament]);
  
  const handleTournamentUpdate = (updatedTournament: Tournament) => {
    setTournament(updatedTournament);
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
              <Button onClick={fetchTournament}>Retry</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href={`/tournaments/${tournament.id}`}>
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Tournament
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold">Manage Tournament</h1>
          <p className="text-gray-600">{tournament.name}</p>
        </div>
      </div>

      <TournamentManagement 
        tournament={tournament}
        onTournamentUpdate={handleTournamentUpdate}
      />
    </div>
  );
}

