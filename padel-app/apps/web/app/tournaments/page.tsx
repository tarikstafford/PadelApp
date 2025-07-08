'use client';

import { useState, useEffect, useContext } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Trophy, Calendar, Users, DollarSign, MapPin, Tag } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import { CategoryBadgeGrid, CategoryEligibilityLegend } from '@/components/tournaments/CategoryBadge';
import { AuthContext } from '@/contexts/AuthContext';

interface Tournament {
  id: number;
  name: string;
  tournament_type: string;
  start_date: string;
  end_date: string;
  status: string;
  total_registered_teams: number;
  max_participants: number;
  entry_fee?: number;
  club_name?: string;
  categories?: {
    id: number;
    category: string;
    max_participants: number;
    min_elo: number;
    max_elo: number;
    current_participants: number;
    current_teams: number;
    current_individuals: number;
  }[];
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
  const { user } = useContext(AuthContext);

  useEffect(() => {
    fetchTournaments();
  }, []);

  const fetchTournaments = async () => {
    try {
      // Use public tournaments endpoint (no authentication required)
      const data = await apiClient.get<Tournament[]>('/tournaments/', {}, null, false);
      setTournaments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
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

  const getAvailableSpots = (tournament: Tournament) => {
    return tournament.max_participants - tournament.total_registered_teams;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground">Tournaments</h1>
            <p className="text-muted-foreground">Discover and join upcoming padel tournaments</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-4 bg-muted rounded w-3/4"></div>
                  <div className="h-3 bg-muted rounded w-1/2"></div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="h-3 bg-muted rounded"></div>
                    <div className="h-3 bg-muted rounded w-5/6"></div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground">Tournaments</h1>
          </div>
          
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
                <Button onClick={fetchTournaments}>Retry</Button>
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground">Tournaments</h1>
          <p className="text-muted-foreground">Discover and join upcoming padel tournaments</p>
          {user && (
            <div className="mt-4">
              <h3 className="text-sm font-medium text-foreground mb-2">Category Eligibility Legend:</h3>
              <CategoryEligibilityLegend />
            </div>
          )}
        </div>

        {tournaments.length === 0 ? (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-12">
                <Trophy className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">No tournaments found</h3>
                <p className="text-muted-foreground">
                  There are currently no tournaments available. Check back later for upcoming tournaments or contact your local clubs to organize new events.
                </p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Featured/Open tournaments */}
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-foreground mb-4">Open for Registration</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {tournaments
                  .filter(t => t.status === 'REGISTRATION_OPEN')
                  .map((tournament) => (
                    <TournamentCard 
                      key={tournament.id} 
                      tournament={tournament} 
                      formatDate={formatDate}
                      formatTournamentType={formatTournamentType}
                      getAvailableSpots={getAvailableSpots}
                      featured={true}
                      userEloRating={user?.elo_rating}
                    />
                  ))}
              </div>
            </div>

            {/* All tournaments */}
            <div>
              <h2 className="text-2xl font-bold text-foreground mb-4">All Tournaments</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {tournaments.map((tournament) => (
                  <TournamentCard 
                    key={tournament.id} 
                    tournament={tournament} 
                    formatDate={formatDate}
                    formatTournamentType={formatTournamentType}
                    getAvailableSpots={getAvailableSpots}
                    userEloRating={user?.elo_rating}
                  />
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function TournamentCard({ 
  tournament, 
  formatDate, 
  formatTournamentType, 
  getAvailableSpots,
  featured = false,
  userEloRating
}: {
  tournament: Tournament;
  formatDate: (date: string) => string;
  formatTournamentType: (type: string) => string;
  getAvailableSpots: (tournament: Tournament) => number;
  featured?: boolean;
  userEloRating?: number;
}) {
  const availableSpots = getAvailableSpots(tournament);
  const isRegistrationOpen = tournament.status === 'REGISTRATION_OPEN';
  
  return (
    <Card className={`hover:shadow-lg transition-shadow ${featured ? 'ring-2 ring-green-500 ring-opacity-50' : ''}`}>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <CardTitle className="text-lg line-clamp-2">{tournament.name}</CardTitle>
            <CardDescription>{formatTournamentType(tournament.tournament_type)}</CardDescription>
          </div>
          <Badge 
            className={`${statusColors[tournament.status as keyof typeof statusColors]} text-white ml-2`}
          >
            {statusLabels[tournament.status as keyof typeof statusLabels]}
          </Badge>
        </div>
        {featured && (
          <Badge variant="outline" className="w-fit bg-green-50 text-green-700 border-green-200">
            Registration Open
          </Badge>
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center text-sm text-muted-foreground">
            <Calendar className="mr-2 h-4 w-4" />
            {formatDate(tournament.start_date)} - {formatDate(tournament.end_date)}
          </div>
          
          <div className="flex items-center text-sm text-muted-foreground">
            <Users className="mr-2 h-4 w-4" />
            {tournament.total_registered_teams} / {tournament.max_participants} teams
            {availableSpots > 0 && isRegistrationOpen && (
              <span className="ml-2 text-green-600 dark:text-green-400 font-medium">
                ({availableSpots} spots left)
              </span>
            )}
          </div>

          {tournament.entry_fee !== undefined && tournament.entry_fee > 0 && (
            <div className="flex items-center text-sm text-muted-foreground">
              <DollarSign className="mr-2 h-4 w-4" />
              ${tournament.entry_fee} entry fee
            </div>
          )}

          {tournament.club_name && (
            <div className="flex items-center text-sm text-muted-foreground">
              <MapPin className="mr-2 h-4 w-4" />
              {tournament.club_name}
            </div>
          )}

          {tournament.categories && tournament.categories.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center text-sm text-muted-foreground">
                <Tag className="mr-2 h-4 w-4" />
                Available Categories
              </div>
              <CategoryBadgeGrid
                categories={tournament.categories}
                userEloRating={userEloRating}
                size="sm"
                showEligibilityIndicator={!!userEloRating}
                showParticipantCount={true}
              />
            </div>
          )}

          <div className="pt-2">
            <Link href={`/tournaments/${tournament.id}`} className="w-full">
              <Button 
                className="w-full" 
                variant={isRegistrationOpen ? "default" : "outline"}
              >
                {isRegistrationOpen ? 'View & Register' : 'View Details'}
              </Button>
            </Link>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}