'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowLeft, Trophy, Calendar, Users, DollarSign, AlertCircle, User } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import { Tournament, TournamentStatus, TournamentType, TournamentCategory, Team, TeamEligibility, TournamentRegistrationRequest } from '@/lib/types';
import { useAuth } from '@/contexts/AuthContext';
import { CategoryBadgeGrid, CategoryEligibilityLegend } from '@/components/tournaments/CategoryBadge';

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
  [TournamentStatus.DRAFT]: 'bg-gray-500',
  [TournamentStatus.REGISTRATION_OPEN]: 'bg-green-500',
  [TournamentStatus.REGISTRATION_CLOSED]: 'bg-yellow-500',
  [TournamentStatus.IN_PROGRESS]: 'bg-blue-500',
  [TournamentStatus.COMPLETED]: 'bg-purple-500',
  [TournamentStatus.CANCELLED]: 'bg-red-500'
};

const CATEGORY_LABELS = {
  [TournamentCategory.BRONZE]: 'Bronze (1.0-2.0)',
  [TournamentCategory.SILVER]: 'Silver (2.0-3.0)',
  [TournamentCategory.GOLD]: 'Gold (3.0-5.0)',
  [TournamentCategory.PLATINUM]: 'Platinum (5.0+)'
};

export default function TournamentDetailsPage() {
  const params = useParams();
  const tournamentId = params.id as string;
  const { user, isAuthenticated } = useAuth();
  
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [userTeams, setUserTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<TournamentCategory | ''>('');
  const [eligibility, setEligibility] = useState<TeamEligibility | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [registering, setRegistering] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTournamentData = useCallback(async () => {
    try {
      // Fetch tournament details (public endpoint, no auth required)
      const data = await apiClient.get<Tournament>(`/tournaments/${tournamentId}`, {}, null, false);
      setTournament(data);

      // Fetch matches (public endpoint, no auth required)
      try {
        const matchesData = await apiClient.get<Match[]>(`/tournaments/${tournamentId}/matches`, {}, null, false);
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

  const fetchUserTeams = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const data = await apiClient.get<Team[]>('/users/me/teams');
      setUserTeams(data);
    } catch (error) {
      console.error('Failed to fetch user teams:', error);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (tournamentId) {
      fetchTournamentData();
      if (isAuthenticated) {
        fetchUserTeams();
      }
    }
  }, [tournamentId, fetchTournamentData, fetchUserTeams, isAuthenticated]);

  const checkEligibility = async (teamId: string) => {
    try {
      const data = await apiClient.get<TeamEligibility>(`/tournaments/${tournamentId}/eligibility/${teamId}`);
      setEligibility(data);
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
    if (!selectedCategory) return;
    if (tournament?.requires_teams && !selectedTeam) return;

    setRegistering(true);
    try {
      const registrationData: TournamentRegistrationRequest = {
        category: selectedCategory as TournamentCategory,
        ...(tournament?.requires_teams && { team_id: parseInt(selectedTeam) }),
      };
      
      await apiClient.post(`/tournaments/${tournamentId}/register`, registrationData);
      
      alert('Successfully registered for tournament!');
      fetchTournamentData(); // Refresh data
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to register');
    } finally {
      setRegistering(false);
    }
  };
  
  const registerIndividually = async (category: TournamentCategory) => {
    setRegistering(true);
    try {
      const registrationData: TournamentRegistrationRequest = {
        category,
      };
      
      await apiClient.post(`/tournaments/${tournamentId}/register`, registrationData);
      
      alert('Successfully registered for tournament!');
      fetchTournamentData(); // Refresh data
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

  const isRegistrationOpen = tournament?.status === TournamentStatus.REGISTRATION_OPEN;
  const isRegistrationDeadlinePassed = tournament && new Date() > new Date(tournament.registration_deadline);
  
  const isAmericano = tournament?.tournament_type === TournamentType.AMERICANO || tournament?.tournament_type === TournamentType.FIXED_AMERICANO;
  const requiresTeams = tournament?.requires_teams;

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

  if (error || !tournament) {
    return (
      <div className="min-h-screen bg-background py-8">
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
                <p className="text-red-600 dark:text-red-400 mb-4">{error || 'Tournament not found'}</p>
                <Button onClick={fetchTournamentData}>Retry</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <Link href="/tournaments">
            <Button variant="ghost" size="sm" className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Tournaments
            </Button>
          </Link>
          
          <div className="flex items-start justify-between">
            <div className="space-y-3">
              <div>
                <h1 className="text-3xl font-bold text-foreground">{tournament.name}</h1>
                <p className="text-muted-foreground text-lg">{formatTournamentType(tournament.tournament_type)}</p>
              </div>
              
              {tournament.categories && tournament.categories.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Available Categories:</p>
                  <CategoryBadgeGrid
                    categories={tournament.categories}
                    userEloRating={user?.elo_rating}
                    size="md"
                    showEligibilityIndicator={!!user}
                    showParticipantCount={true}
                  />
                  {user && (
                    <CategoryEligibilityLegend className="text-xs" />
                  )}
                </div>
              )}
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
                  <p className="text-foreground">{tournament.description}</p>
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
                        <Calendar className="h-5 w-5 text-muted-foreground mr-3" />
                        <div>
                          <p className="font-medium">Start Date</p>
                          <p className="text-muted-foreground">{formatDate(tournament.start_date)}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <Calendar className="h-5 w-5 text-muted-foreground mr-3" />
                        <div>
                          <p className="font-medium">End Date</p>
                          <p className="text-muted-foreground">{formatDate(tournament.end_date)}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <Users className="h-5 w-5 text-muted-foreground mr-3" />
                        <div>
                          <p className="font-medium">{requiresTeams ? 'Teams' : 'Players'}</p>
                          <p className="text-muted-foreground">
                            {requiresTeams ? tournament.total_registered_teams : tournament.total_registered_participants} / {tournament.max_participants}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <DollarSign className="h-5 w-5 text-muted-foreground mr-3" />
                        <div>
                          <p className="font-medium">Entry Fee</p>
                          <p className="text-muted-foreground">${tournament.entry_fee}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="pt-4 border-t">
                      <p className="font-medium mb-1">Registration Deadline</p>
                      <p className="text-muted-foreground">{formatDate(tournament.registration_deadline)}</p>
                      {isRegistrationDeadlinePassed && (
                        <p className="text-red-600 dark:text-red-400 text-sm mt-1">Registration deadline has passed</p>
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
                    <div className="space-y-6">
                      {user && (
                        <div>
                          <h4 className="font-medium mb-2">Your Eligibility</h4>
                          <CategoryEligibilityLegend />
                        </div>
                      )}
                      
                      <div>
                        <h4 className="font-medium mb-3">Available Categories</h4>
                        <CategoryBadgeGrid
                          categories={tournament.categories}
                          userEloRating={user?.elo_rating}
                          size="lg"
                          showEligibilityIndicator={!!user}
                          showParticipantCount={true}
                        />
                      </div>
                      
                      <div className="grid gap-4">
                        {tournament.categories.map((category) => (
                          <div key={category.id} className="p-4 border rounded-lg">
                            <div className="flex justify-between items-start">
                              <div>
                                <h4 className="font-medium text-lg">
                                  {CATEGORY_LABELS[category.category as keyof typeof CATEGORY_LABELS]} Category
                                </h4>
                                <p className="text-muted-foreground">
                                  ELO Range: {category.min_elo} - {category.max_elo === Infinity ? '∞' : category.max_elo}
                                </p>
                              </div>
                              <Badge variant="outline">
                                {requiresTeams ? category.current_teams : category.current_individuals} / {category.max_participants} {requiresTeams ? 'teams' : 'players'}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
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
                      <div className="text-center py-8 text-muted-foreground">
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
                                <p className="text-muted-foreground">
                                  {match.team1_name} vs {match.team2_name}
                                </p>
                                {match.scheduled_time && (
                                  <p className="text-sm text-muted-foreground">
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
            {isRegistrationOpen && !isRegistrationDeadlinePassed && isAuthenticated && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    {requiresTeams ? <Users className="h-5 w-5" /> : <User className="h-5 w-5" />}
                    {requiresTeams ? 'Register Your Team' : 'Individual Registration'}
                  </CardTitle>
                  <CardDescription>
                    {requiresTeams 
                      ? 'Join this tournament with one of your teams'
                      : 'Register as an individual player for this Americano tournament'
                    }
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {requiresTeams ? (
                    /* Team Registration */
                    userTeams.length === 0 ? (
                      <div className="text-center py-4">
                        <AlertCircle className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
                        <p className="text-sm text-muted-foreground">
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
                            {eligibility.eligible_categories.length > 0 ? (
                              <>
                                <label className="block text-sm font-medium mb-2">Select Category</label>
                                <Select value={selectedCategory} onValueChange={(value) => setSelectedCategory(value as TournamentCategory)}>
                                  <SelectTrigger>
                                    <SelectValue placeholder="Choose category" />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {eligibility.eligible_categories.map((category) => (
                                      <SelectItem key={category} value={category}>
                                        {CATEGORY_LABELS[category]}
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
                                <p className="text-xs text-red-600 mt-1">
                                  {Object.entries(eligibility.reasons).map(([cat, reason]) => (
                                    `${cat}: ${reason}`
                                  )).join(', ')}
                                </p>
                              </div>
                            )}
                          </div>
                        )}
                      </>
                    )
                  ) : (
                    /* Individual Registration */
                    <div className="space-y-4">
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <p className="text-sm text-blue-800">
                          Your ELO Rating: {user?.elo_rating?.toFixed(2) || 'N/A'}
                        </p>
                        <p className="text-xs text-blue-600 mt-1">
                          Register for categories that match your skill level
                        </p>
                      </div>
                      
                      <div className="space-y-2">
                        <label className="block text-sm font-medium">Available Categories</label>
                        {tournament?.categories
                          .filter(cat => {
                            const userElo = user?.elo_rating || 0;
                            return userElo >= cat.min_elo && userElo <= cat.max_elo;
                          })
                          .map((category) => (
                            <div key={category.id} className="border rounded-lg p-3">
                              <div className="flex justify-between items-center">
                                <div>
                                  <p className="font-medium">{CATEGORY_LABELS[category.category]}</p>
                                  <p className="text-xs text-muted-foreground">
                                    {category.current_individuals}/{category.max_participants} registered
                                  </p>
                                </div>
                                <Button
                                  size="sm"
                                  onClick={() => registerIndividually(category.category)}
                                  disabled={registering || category.current_individuals >= category.max_participants}
                                >
                                  {registering ? 'Registering...' : category.current_individuals >= category.max_participants ? 'Full' : 'Register'}
                                </Button>
                              </div>
                            </div>
                          ))}
                        
                        {tournament?.categories.filter(cat => {
                          const userElo = user?.elo_rating || 0;
                          return userElo >= cat.min_elo && userElo <= cat.max_elo;
                        }).length === 0 && (
                          <div className="text-center py-4">
                            <AlertCircle className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
                            <p className="text-sm text-muted-foreground">
                              No categories available for your ELO rating ({user?.elo_rating?.toFixed(2) || 'N/A'})
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
            
            {isRegistrationOpen && !isRegistrationDeadlinePassed && !isAuthenticated && (
              <Card>
                <CardHeader>
                  <CardTitle>Registration Required</CardTitle>
                  <CardDescription>Sign in to register for this tournament</CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/auth/login">
                    <Button className="w-full">Sign In to Register</Button>
                  </Link>
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
                  <span className="text-muted-foreground">
                    {requiresTeams ? 'Registered Teams' : 'Registered Players'}
                  </span>
                  <span className="font-medium">
                    {requiresTeams ? tournament.total_registered_teams : tournament.total_registered_participants}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Available Spots</span>
                  <span className="font-medium">
                    {tournament.max_participants - (requiresTeams ? tournament.total_registered_teams : tournament.total_registered_participants)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Entry Fee</span>
                  <span className="font-medium">${tournament.entry_fee}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Categories</span>
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