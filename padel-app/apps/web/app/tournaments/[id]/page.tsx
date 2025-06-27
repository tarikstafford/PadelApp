'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowLeft, Trophy, Calendar, Users, DollarSign, MapPin, AlertCircle } from 'lucide-react';
import Link from 'next/link';

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
  name: string;
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
}

const statusColors = {
  DRAFT: 'bg-gray-500',
  REGISTRATION_OPEN: 'bg-green-500',
  REGISTRATION_CLOSED: 'bg-yellow-500',
  IN_PROGRESS: 'bg-blue-500',
  COMPLETED: 'bg-purple-500',
  CANCELLED: 'bg-red-500'
};

const CATEGORY_LABELS = {
  BRONZE: 'Bronze',
  SILVER: 'Silver',
  GOLD: 'Gold',
  PLATINUM: 'Platinum'
};

export default function TournamentDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const tournamentId = params.id as string;
  
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [userTeams, setUserTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [eligibility, setEligibility] = useState<any>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [registering, setRegistering] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (tournamentId) {
      fetchTournamentData();
      fetchUserTeams();
    }
  }, [tournamentId]);

  const fetchTournamentData = async () => {
    try {
      const response = await fetch(`/api/v1/tournaments/${tournamentId}`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch tournament details');
      }

      const data = await response.json();
      setTournament(data);

      // Fetch matches
      const matchesResponse = await fetch(`/api/v1/tournaments/${tournamentId}/matches`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (matchesResponse.ok) {
        const matchesData = await matchesResponse.json();
        setMatches(matchesData);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const fetchUserTeams = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch('/api/v1/users/me/teams', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUserTeams(data);
      }
    } catch (error) {
      console.error('Failed to fetch user teams:', error);
    }
  };

  const checkEligibility = async (teamId: string) => {
    try {
      const response = await fetch(`/api/v1/tournaments/${tournamentId}/eligibility/${teamId}`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setEligibility(data);
      }
    } catch (error) {
      console.error('Failed to check eligibility:', error);
    }
  };

  const handleTeamSelection = (teamId: string) => {
    setSelectedTeam(teamId);
    setSelectedCategory('');
    setEligibility(null);
    if (teamId) {
      checkEligibility(teamId);
    }
  };

  const registerForTournament = async () => {
    if (!selectedTeam || !selectedCategory) return;

    setRegistering(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1/tournaments/${tournamentId}/register`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          team_id: parseInt(selectedTeam),
          category: selectedCategory,
        }),
      });

      if (response.ok) {
        alert('Successfully registered for tournament!');
        fetchTournamentData(); // Refresh data
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to register for tournament');
      }
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to register');
    } finally {
      setRegistering(false);
    }
  };

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

  const isRegistrationOpen = tournament?.status === 'REGISTRATION_OPEN';
  const isRegistrationDeadlinePassed = tournament && new Date() > new Date(tournament.registration_deadline);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !tournament) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Link href="/tournaments">
            <Button variant="ghost" size="sm" className="mb-4">
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
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <Link href="/tournaments">
            <Button variant="ghost" size="sm" className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Tournaments
            </Button>
          </Link>
          
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{tournament.name}</h1>
              <p className="text-gray-600 text-lg">{formatTournamentType(tournament.tournament_type)}</p>
            </div>
            <Badge className={`${statusColors[tournament.status as keyof typeof statusColors]} text-white`}>
              {getStatusLabel(tournament.status)}
            </Badge>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
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

            <Tabs defaultValue="details" className="space-y-6">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="details">Details</TabsTrigger>
                <TabsTrigger value="categories">Categories</TabsTrigger>
                <TabsTrigger value="matches">Matches</TabsTrigger>
              </TabsList>

              <TabsContent value="details">
                <Card>
                  <CardHeader>
                    <CardTitle>Tournament Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="flex items-center">
                        <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <p className="font-medium">Start Date</p>
                          <p className="text-gray-600">{formatDate(tournament.start_date)}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <p className="font-medium">End Date</p>
                          <p className="text-gray-600">{formatDate(tournament.end_date)}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <Users className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <p className="font-medium">Teams</p>
                          <p className="text-gray-600">
                            {tournament.total_registered_teams} / {tournament.max_participants}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <DollarSign className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <p className="font-medium">Entry Fee</p>
                          <p className="text-gray-600">${tournament.entry_fee}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="pt-4 border-t">
                      <p className="font-medium mb-1">Registration Deadline</p>
                      <p className="text-gray-600">{formatDate(tournament.registration_deadline)}</p>
                      {isRegistrationDeadlinePassed && (
                        <p className="text-red-600 text-sm mt-1">Registration deadline has passed</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="categories">
                <Card>
                  <CardHeader>
                    <CardTitle>Tournament Categories</CardTitle>
                    <CardDescription>Teams are divided into categories based on average ELO rating</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {tournament.categories.map((category) => (
                        <div key={category.id} className="p-4 border rounded-lg">
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="font-medium text-lg">
                                {CATEGORY_LABELS[category.category as keyof typeof CATEGORY_LABELS]} Category
                              </h4>
                              <p className="text-gray-600">
                                ELO Range: {category.min_elo} - {category.max_elo === Infinity ? '∞' : category.max_elo}
                              </p>
                            </div>
                            <Badge variant="outline">
                              {category.current_participants} / {category.max_participants} teams
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="matches">
                <Card>
                  <CardHeader>
                    <CardTitle>Tournament Matches</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {matches.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <Trophy className="mx-auto h-12 w-12 mb-4" />
                        <p>Matches will appear here once the tournament begins</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {matches.map((match) => (
                          <div key={match.id} className="p-4 border rounded-lg">
                            <div className="flex justify-between items-start">
                              <div>
                                <h4 className="font-medium">
                                  Round {match.round_number}, Match {match.match_number}
                                </h4>
                                <p className="text-gray-600">
                                  {match.team1_name} vs {match.team2_name}
                                </p>
                                {match.scheduled_time && (
                                  <p className="text-sm text-gray-500">
                                    {formatDate(match.scheduled_time)} | {match.court_name}
                                  </p>
                                )}
                              </div>
                              <div className="text-right">
                                <Badge variant={match.status === 'COMPLETED' ? 'default' : 'outline'}>
                                  {match.status}
                                </Badge>
                                {match.status === 'COMPLETED' && (
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
            </Tabs>
          </div>

          {/* Registration Sidebar */}
          <div className="space-y-6">
            {isRegistrationOpen && !isRegistrationDeadlinePassed && (
              <Card>
                <CardHeader>
                  <CardTitle>Register Your Team</CardTitle>
                  <CardDescription>Join this tournament with one of your teams</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {userTeams.length === 0 ? (
                    <div className="text-center py-4">
                      <AlertCircle className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                      <p className="text-sm text-gray-600">
                        You need to create a team first to register for tournaments.
                      </p>
                      <Link href="/teams/create" className="mt-2 inline-block">
                        <Button size="sm">Create Team</Button>
                      </Link>
                    </div>
                  ) : (
                    <>
                      <div>
                        <label className="block text-sm font-medium mb-2">Select Team</label>
                        <Select value={selectedTeam} onValueChange={handleTeamSelection}>
                          <SelectTrigger>
                            <SelectValue placeholder="Choose your team" />
                          </SelectTrigger>
                          <SelectContent>
                            {userTeams.map((team) => (
                              <SelectItem key={team.id} value={team.id.toString()}>
                                {team.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      {eligibility && (
                        <div>
                          {eligibility.eligible ? (
                            <>
                              <label className="block text-sm font-medium mb-2">Select Category</label>
                              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                                <SelectTrigger>
                                  <SelectValue placeholder="Choose category" />
                                </SelectTrigger>
                                <SelectContent>
                                  {eligibility.eligible_categories.map((category: string) => (
                                    <SelectItem key={category} value={category}>
                                      {CATEGORY_LABELS[category as keyof typeof CATEGORY_LABELS]}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                              
                              <div className="mt-4 p-3 bg-green-50 rounded-lg">
                                <p className="text-sm text-green-800">
                                  Team Average ELO: {eligibility.average_elo.toFixed(2)}
                                </p>
                                <p className="text-xs text-green-600 mt-1">
                                  Your team is eligible for {eligibility.eligible_categories.length} category(s)
                                </p>
                              </div>

                              <Button 
                                className="w-full"
                                onClick={registerForTournament}
                                disabled={!selectedCategory || registering}
                              >
                                {registering ? 'Registering...' : 'Register Team'}
                              </Button>
                            </>
                          ) : (
                            <div className="p-3 bg-red-50 rounded-lg">
                              <p className="text-sm text-red-800">
                                This team is not eligible for this tournament.
                              </p>
                              <p className="text-xs text-red-600 mt-1">
                                Team Average ELO: {eligibility.average_elo.toFixed(2)}
                              </p>
                            </div>
                          )}
                        </div>
                      )}
                    </>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Tournament Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Registered Teams</span>
                  <span className="font-medium">{tournament.total_registered_teams}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Available Spots</span>
                  <span className="font-medium">{tournament.max_participants - tournament.total_registered_teams}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Entry Fee</span>
                  <span className="font-medium">${tournament.entry_fee}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Categories</span>
                  <span className="font-medium">{tournament.categories.length}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}