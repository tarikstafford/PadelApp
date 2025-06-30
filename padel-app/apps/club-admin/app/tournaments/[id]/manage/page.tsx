'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowLeft, Play, Square, Trophy, Calendar, RefreshCw } from 'lucide-react';
import Link from 'next/link';

interface Tournament {
  id: number;
  name: string;
  status: string;
  tournament_type: string;
}

interface Match {
  id: number;
  tournament_id: number;
  category: string;
  team1_id: number;
  team2_id: number;
  team1_name: string;
  team2_name: string;
  round_number: number;
  match_number: number;
  scheduled_time: string;
  court_id: number;
  court_name: string;
  status: string;
  winning_team_id: number;
  team1_score: number;
  team2_score: number;
}

interface Court {
  id: number;
  name: string;
}

const TOURNAMENT_STATUSES = [
  { value: 'DRAFT', label: 'Draft' },
  { value: 'REGISTRATION_OPEN', label: 'Registration Open' },
  { value: 'REGISTRATION_CLOSED', label: 'Registration Closed' },
  { value: 'IN_PROGRESS', label: 'In Progress' },
  { value: 'COMPLETED', label: 'Completed' },
  { value: 'CANCELLED', label: 'Cancelled' },
];

const MATCH_STATUSES = [
  { value: 'SCHEDULED', label: 'Scheduled' },
  { value: 'IN_PROGRESS', label: 'In Progress' },
  { value: 'COMPLETED', label: 'Completed' },
  { value: 'CANCELLED', label: 'Cancelled' },
  { value: 'WALKOVER', label: 'Walkover' },
];

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export default function TournamentManagePage() {
  const params = useParams();
  const router = useRouter();
  const tournamentId = params.id as string;
  
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [courts, setCourts] = useState<Court[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (tournamentId) {
      fetchData();
    }
  }, [tournamentId]);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch tournament, matches, and courts in parallel
      const [tournamentRes, matchesRes, courtsRes] = await Promise.all([
        fetch(`/api/v1/tournaments/${tournamentId}`, {
          headers: { 'Authorization': `Bearer ${token}` },
        }),
        fetch(`/api/v1/tournaments/${tournamentId}/matches`, {
          headers: { 'Authorization': `Bearer ${token}` },
        }),
        fetch('/api/v1/courts', {
          headers: { 'Authorization': `Bearer ${token}` },
        }),
      ]);

      if (!tournamentRes.ok) {
        throw new Error('Failed to fetch tournament');
      }

      const tournamentData = await tournamentRes.json();
      setTournament(tournamentData);

      if (matchesRes.ok) {
        const matchesData = await matchesRes.json();
        setMatches(matchesData);
      }

      if (courtsRes.ok) {
        const courtsData = await courtsRes.json();
        setCourts(courtsData);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const updateTournamentStatus = async (newStatus: string) => {
    try {
      setUpdating(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(`/api/v1/tournaments/${tournamentId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        throw new Error('Failed to update tournament status');
      }

      const updatedTournament = await response.json();
      setTournament(updatedTournament);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update tournament');
    } finally {
      setUpdating(false);
    }
  };

  const generateBracket = async () => {
    try {
      setUpdating(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(`/api/v1/tournaments/${tournamentId}/generate-bracket?category_config_id=1`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to generate bracket');
      }

      await fetchData(); // Refresh data
      alert('Bracket generated successfully!');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to generate bracket');
    } finally {
      setUpdating(false);
    }
  };

  const updateMatchResult = async (matchId: number, team1Score: number, team2Score: number, winningTeamId: number) => {
    try {
      const token = localStorage.getItem('token');
      
      const response = await fetch(`/api/v1/tournaments/matches/${matchId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          team1_score: team1Score,
          team2_score: team2Score,
          winning_team_id: winningTeamId,
          status: 'COMPLETED',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update match result');
      }

      await fetchData(); // Refresh data
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update match');
    }
  };

  const scheduleMatch = async (matchId: number, courtId: number, scheduledTime: string) => {
    try {
      const token = localStorage.getItem('token');
      
      const response = await fetch(`/api/v1/tournaments/matches/${matchId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          court_id: courtId,
          scheduled_time: scheduledTime,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to schedule match');
      }

      await fetchData(); // Refresh data
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to schedule match');
    }
  };

  const finalizeTournament = async () => {
    if (!confirm('Are you sure you want to finalize this tournament? This action cannot be undone.')) {
      return;
    }

    try {
      setUpdating(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(`/api/v1/tournaments/${tournamentId}/finalize`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to finalize tournament');
      }

      await fetchData(); // Refresh data
      alert('Tournament finalized successfully! Trophies have been awarded.');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to finalize tournament');
    } finally {
      setUpdating(false);
    }
  };

  const groupMatchesByRound = (matches: Match[]) => {
    return matches.reduce((acc, match) => {
      const key = `Round ${match.round_number}`;
      if (!acc[key]) {
        acc[key] = [];
      }
      acc[key].push(match);
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
              <Button onClick={fetchData}>Retry</Button>
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
        <Button onClick={fetchData} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Tournament Controls</CardTitle>
          <CardDescription>Manage tournament status and generate brackets</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <Label htmlFor="status">Tournament Status</Label>
              <Select 
                value={tournament.status} 
                onValueChange={updateTournamentStatus}
                disabled={updating}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TOURNAMENT_STATUSES.map((status) => (
                    <SelectItem key={status.value} value={status.value}>
                      {status.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex gap-4">
            <Button 
              onClick={generateBracket}
              disabled={updating || tournament.status === 'COMPLETED'}
            >
              <Play className="h-4 w-4 mr-2" />
              Generate Bracket
            </Button>
            
            {tournament.status === 'IN_PROGRESS' && (
              <Button 
                onClick={finalizeTournament}
                disabled={updating}
                variant="outline"
              >
                <Trophy className="h-4 w-4 mr-2" />
                Finalize Tournament
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="matches" className="space-y-6">
        <TabsList>
          <TabsTrigger value="matches">Match Management</TabsTrigger>
          <TabsTrigger value="schedule">Schedule Matches</TabsTrigger>
        </TabsList>

        <TabsContent value="matches">
          <div className="space-y-6">
            {Object.entries(groupMatchesByRound(matches)).map(([round, roundMatches]) => (
              <Card key={round}>
                <CardHeader>
                  <CardTitle>{round}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {roundMatches.map((match) => (
                      <MatchCard 
                        key={match.id} 
                        match={match} 
                        onUpdateResult={updateMatchResult}
                      />
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="schedule">
          <Card>
            <CardHeader>
              <CardTitle>Schedule Matches</CardTitle>
              <CardDescription>Assign courts and times to matches</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {matches.filter(m => m.status === 'SCHEDULED' && !m.scheduled_time).map((match) => (
                  <ScheduleMatchCard 
                    key={match.id} 
                    match={match} 
                    courts={courts}
                    onSchedule={scheduleMatch}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

function MatchCard({ match, onUpdateResult }: { 
  match: Match, 
  onUpdateResult: (matchId: number, team1Score: number, team2Score: number, winningTeamId: number) => void 
}) {
  const [team1Score, setTeam1Score] = useState(match.team1_score || 0);
  const [team2Score, setTeam2Score] = useState(match.team2_score || 0);

  const handleSubmitResult = () => {
    const winningTeamId = team1Score > team2Score ? match.team1_id : match.team2_id;
    onUpdateResult(match.id, team1Score, team2Score, winningTeamId);
  };

  return (
    <div className="p-4 border rounded-lg">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="font-medium">Match {match.match_number}</h4>
          <p className="text-sm text-gray-600">
            {match.team1_name} vs {match.team2_name}
          </p>
          {match.scheduled_time && (
            <p className="text-xs text-gray-500">
              {formatDate(match.scheduled_time)} | {match.court_name}
            </p>
          )}
        </div>
        
        <div className="flex items-center gap-4">
          <Badge variant={match.status === 'COMPLETED' ? 'default' : 'outline'}>
            {match.status}
          </Badge>
          
          {match.status !== 'COMPLETED' && match.team1_id && match.team2_id && (
            <div className="flex items-center gap-2">
              <Input
                type="number"
                min="0"
                max="20"
                value={team1Score}
                onChange={(e) => setTeam1Score(parseInt(e.target.value) || 0)}
                className="w-16"
              />
              <span>-</span>
              <Input
                type="number"
                min="0"
                max="20"
                value={team2Score}
                onChange={(e) => setTeam2Score(parseInt(e.target.value) || 0)}
                className="w-16"
              />
              <Button size="sm" onClick={handleSubmitResult}>
                Submit Result
              </Button>
            </div>
          )}
          
          {match.status === 'COMPLETED' && (
            <div className="text-sm font-medium">
              {match.team1_score} - {match.team2_score}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ScheduleMatchCard({ match, courts, onSchedule }: { 
  match: Match, 
  courts: Court[], 
  onSchedule: (matchId: number, courtId: number, scheduledTime: string) => void 
}) {
  const [selectedCourt, setSelectedCourt] = useState('');
  const [scheduledTime, setScheduledTime] = useState('');

  const handleSchedule = () => {
    if (selectedCourt && scheduledTime) {
      onSchedule(match.id, parseInt(selectedCourt), scheduledTime);
    }
  };

  return (
    <div className="p-4 border rounded-lg">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="font-medium">
            Round {match.round_number}, Match {match.match_number}
          </h4>
          <p className="text-sm text-gray-600">
            {match.team1_name} vs {match.team2_name}
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Select value={selectedCourt} onValueChange={setSelectedCourt}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Court" />
            </SelectTrigger>
            <SelectContent>
              {courts.map((court) => (
                <SelectItem key={court.id} value={court.id.toString()}>
                  {court.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Input
            type="datetime-local"
            value={scheduledTime}
            onChange={(e) => setScheduledTime(e.target.value)}
            className="w-48"
          />
          
          <Button 
            size="sm" 
            onClick={handleSchedule}
            disabled={!selectedCourt || !scheduledTime}
          >
            <Calendar className="h-4 w-4 mr-2" />
            Schedule
          </Button>
        </div>
      </div>
    </div>
  );
}