'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Users, 
  Trophy, 
  Settings, 
  Play, 
  Pause,
  UserCheck,
  Clock,
  MapPin
} from 'lucide-react';
import { Tournament, TournamentStatus, TournamentTeam, TournamentParticipant, TournamentMatch, User } from '@/lib/types';
import { apiClient } from '@/lib/api';
import { format } from 'date-fns';

interface TournamentManagementProps {
  tournament: Tournament;
  onTournamentUpdate: (tournament: Tournament) => void;
}

const statusColors = {
  [TournamentStatus.DRAFT]: 'bg-gray-500',
  [TournamentStatus.REGISTRATION_OPEN]: 'bg-green-500',
  [TournamentStatus.REGISTRATION_CLOSED]: 'bg-yellow-500',
  [TournamentStatus.IN_PROGRESS]: 'bg-blue-500',
  [TournamentStatus.COMPLETED]: 'bg-purple-500',
  [TournamentStatus.CANCELLED]: 'bg-red-500',
};

export default function TournamentManagement({ 
  tournament, 
  onTournamentUpdate 
}: TournamentManagementProps) {
  const [teams, setTeams] = useState<TournamentTeam[]>([]);
  const [participants, setParticipants] = useState<TournamentParticipant[]>([]);
  const [matches, setMatches] = useState<TournamentMatch[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchTournamentData = useCallback(async () => {
    setLoading(true);
    try {
      // Fetch teams or participants based on tournament type
      if (tournament.requires_teams) {
        const teamsData = await apiClient.get<TournamentTeam[]>(`/tournaments/${tournament.id}/teams`);
        setTeams(teamsData);
      } else {
        const participantsData = await apiClient.get<TournamentParticipant[]>(`/tournaments/${tournament.id}/participants`);
        setParticipants(participantsData);
      }

      // Fetch matches
      try {
        const matchesData = await apiClient.get<TournamentMatch[]>(`/tournaments/${tournament.id}/matches`);
        setMatches(matchesData);
      } catch (error) {
        console.warn('Could not fetch matches:', error);
        setMatches([]);
      }
    } catch (error) {
      console.error('Failed to fetch tournament data:', error);
    } finally {
      setLoading(false);
    }
  }, [tournament.id, tournament.requires_teams]);

  useEffect(() => {
    fetchTournamentData();
  }, [fetchTournamentData]);

  const updateTournamentStatus = async (status: TournamentStatus) => {
    try {
      const updatedTournament = await apiClient.patch<Tournament>(`/tournaments/${tournament.id}`, {
        status,
      });
      onTournamentUpdate(updatedTournament);
    } catch (error) {
      console.error('Failed to update tournament status:', error);
      alert('Failed to update tournament status');
    }
  };

  const generateBrackets = async () => {
    setLoading(true);
    try {
      await apiClient.post(`/tournaments/${tournament.id}/generate-brackets`, {});
      await fetchTournamentData();
      alert('Tournament brackets generated successfully!');
    } catch (error) {
      console.error('Failed to generate brackets:', error);
      alert('Failed to generate brackets');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'MMM d, yyyy h:mm a');
  };

  const canStartTournament = tournament.status === TournamentStatus.REGISTRATION_CLOSED || 
                            tournament.status === TournamentStatus.DRAFT;
  const canCloseRegistration = tournament.status === TournamentStatus.REGISTRATION_OPEN;
  const canOpenRegistration = tournament.status === TournamentStatus.DRAFT || 
                              tournament.status === TournamentStatus.REGISTRATION_CLOSED;

  return (
    <div className="space-y-6">
      {/* Tournament Status and Actions */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Tournament Management</CardTitle>
              <CardDescription>
                Manage {tournament.name} - Current status: {tournament.status.replace('_', ' ').toLowerCase()}
              </CardDescription>
            </div>
            <Badge className={`${statusColors[tournament.status]} text-white`}>
              {tournament.status.replace('_', ' ')}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {canOpenRegistration && (
              <Button 
                variant="outline"
                onClick={() => updateTournamentStatus(TournamentStatus.REGISTRATION_OPEN)}
              >
                <Play className="mr-2 h-4 w-4" />
                Open Registration
              </Button>
            )}
            
            {canCloseRegistration && (
              <Button 
                variant="outline"
                onClick={() => updateTournamentStatus(TournamentStatus.REGISTRATION_CLOSED)}
              >
                <Pause className="mr-2 h-4 w-4" />
                Close Registration
              </Button>
            )}
            
            {canStartTournament && (
              <>
                <Button onClick={generateBrackets} disabled={loading}>
                  <Trophy className="mr-2 h-4 w-4" />
                  Generate Brackets
                </Button>
                <Button 
                  onClick={() => updateTournamentStatus(TournamentStatus.IN_PROGRESS)}
                >
                  <Play className="mr-2 h-4 w-4" />
                  Start Tournament
                </Button>
              </>
            )}
            
            {tournament.status === TournamentStatus.IN_PROGRESS && (
              <Button 
                onClick={() => updateTournamentStatus(TournamentStatus.COMPLETED)}
                variant="outline"
              >
                <Trophy className="mr-2 h-4 w-4" />
                Complete Tournament
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Tournament Details Tabs */}
      <Tabs defaultValue="participants" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="participants">
            {tournament.requires_teams ? 'Teams' : 'Participants'}
          </TabsTrigger>
          <TabsTrigger value="matches">Matches</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="participants">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                {tournament.requires_teams ? 'Registered Teams' : 'Registered Participants'}
              </CardTitle>
              <CardDescription>
                {tournament.requires_teams ? teams.length : participants.length} of {tournament.max_participants} spots filled
              </CardDescription>
            </CardHeader>
            <CardContent>
              {tournament.requires_teams ? (
                <div className="space-y-4">
                  {teams.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <Users className="mx-auto h-12 w-12 mb-4" />
                      <p>No teams registered yet</p>
                    </div>
                  ) : (
                    teams.map((team) => (
                      <div key={team.id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-medium">{team.team_name}</h4>
                            <p className="text-sm text-muted-foreground">
                              Category: {team.category} • Average ELO: {team.average_elo.toFixed(2)}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Registered: {formatDate(team.registration_date)}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            {team.seed && (
                              <Badge variant="outline">Seed #{team.seed}</Badge>
                            )}
                            <Badge variant={team.is_active ? 'default' : 'secondary'}>
                              {team.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </div>
                        </div>
                        <div className="mt-3">
                          <p className="text-sm font-medium mb-2">Players:</p>
                          <div className="flex flex-wrap gap-2">
                            {team.players.map((player: User) => (
                              <Badge key={player.id} variant="outline">
                                {player.full_name || player.email}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  {participants.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <UserCheck className="mx-auto h-12 w-12 mb-4" />
                      <p>No participants registered yet</p>
                    </div>
                  ) : (
                    participants.map((participant) => (
                      <div key={participant.id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-medium">{participant.user_name}</h4>
                            <p className="text-sm text-muted-foreground">
                              {participant.user_email}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              Category: {participant.category} • ELO: {participant.elo_rating.toFixed(2)}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Registered: {formatDate(participant.registration_date)}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            {participant.seed && (
                              <Badge variant="outline">Seed #{participant.seed}</Badge>
                            )}
                            <Badge variant={participant.is_active ? 'default' : 'secondary'}>
                              {participant.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="matches">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="h-5 w-5" />
                Tournament Matches
              </CardTitle>
              <CardDescription>
                {matches.length} matches scheduled
              </CardDescription>
            </CardHeader>
            <CardContent>
              {matches.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Trophy className="mx-auto h-12 w-12 mb-4" />
                  <p>No matches scheduled yet</p>
                  <p className="text-sm">Generate brackets to create matches</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {matches.map((match) => (
                    <div key={match.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-medium">
                            Round {match.round_number}, Match {match.match_number}
                          </h4>
                          <p className="text-sm text-muted-foreground">
                            {match.team1_name || 'TBD'} vs {match.team2_name || 'TBD'}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            Category: {match.category}
                          </p>
                          {match.scheduled_time && (
                            <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                              <Clock className="h-3 w-3" />
                              {formatDate(match.scheduled_time)}
                              {match.court_name && (
                                <>
                                  <MapPin className="h-3 w-3 ml-2" />
                                  {match.court_name}
                                </>
                              )}
                            </div>
                          )}
                        </div>
                        <div className="text-right">
                          <Badge variant="outline">
                            {match.status}
                          </Badge>
                          {match.team1_score !== undefined && match.team2_score !== undefined && (
                            <p className="text-sm mt-1">
                              {match.team1_score} - {match.team2_score}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Tournament Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="font-medium">Start Date</p>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(tournament.start_date)}
                  </p>
                </div>
                <div>
                  <p className="font-medium">End Date</p>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(tournament.end_date)}
                  </p>
                </div>
                <div>
                  <p className="font-medium">Registration Deadline</p>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(tournament.registration_deadline)}
                  </p>
                </div>
                <div>
                  <p className="font-medium">Entry Fee</p>
                  <p className="text-sm text-muted-foreground">
                    ${tournament.entry_fee.toFixed(2)}
                  </p>
                </div>
              </div>
              
              <div>
                <p className="font-medium mb-2">Categories</p>
                <div className="space-y-2">
                  {tournament.categories.map((category) => (
                    <div key={category.id} className="flex justify-between items-center p-2 border rounded">
                      <span>{category.category}</span>
                      <span className="text-sm text-muted-foreground">
                        {tournament.requires_teams ? category.current_teams : category.current_individuals} / {category.max_participants}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}