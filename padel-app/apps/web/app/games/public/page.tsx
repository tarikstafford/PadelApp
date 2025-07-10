"use client";

import React, { useState, useEffect, useCallback, Suspense } from 'react';
import Link from 'next/link';
import { Button } from "@workspace/ui/components/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@workspace/ui/components/card";
import { Calendar } from "@workspace/ui/components/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@workspace/ui/components/popover";
import { Badge } from "@workspace/ui/components/badge";
import { Label } from "@workspace/ui/components/label";
import { Loader2, AlertTriangle, CalendarIcon, Users, UserPlus } from 'lucide-react'; // Removed unused icons
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import withAuth from '@/components/auth/withAuth';
import { format, parseISO } from 'date-fns';

// Interfaces matching backend GameResponse structure
interface UserForGamePlayer {
    id: number;
    name?: string | null;
    email: string;
}
interface GamePlayer {
    user: UserForGamePlayer;
    status: string; 
}
interface BookingForGame {
    id: number;
    court_id: number;
    user_id: number;
    start_time: string; 
    end_time: string;
    court?: { name?: string | null, club?: { name?: string | null, city?: string | null } };
}
interface PublicGame {
    id: number;
    booking: BookingForGame;
    game_type: "PRIVATE" | "PUBLIC";
    skill_level?: string | null;
    players: GamePlayer[]; // List of accepted players primarily, or all for slot calculation
}

const MAX_PLAYERS_PER_GAME = 4;
const ITEMS_PER_PAGE = 9;
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

function PublicGamesPageInternal() {
  const { user: currentUser, accessToken } = useAuth();

  const [publicGames, setPublicGames] = useState<PublicGame[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [currentPage, setCurrentPage] = useState(1);
  const [hasNextPage, setHasNextPage] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(undefined);
  const [joinRequestLoading, setJoinRequestLoading] = useState<Record<number, boolean>>({});

  const fetchPublicGames = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.append('skip', ((currentPage - 1) * ITEMS_PER_PAGE).toString());
      params.append('limit', (ITEMS_PER_PAGE + 1).toString());
      if (selectedDate) {
        params.append('target_date', format(selectedDate, 'yyyy-MM-dd'));
      }
      params.append('future_only', 'true');
      const response = await fetch(`${API_BASE_URL}/api/v1/games/public?${params.toString()}`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to fetch public games" }));
        const errorMessage = typeof errorData.detail === 'string' ? errorData.detail : "Failed to fetch public games";
        throw new Error(errorMessage);
      }
      const data: PublicGame[] = await response.json();
      
      if (data.length > ITEMS_PER_PAGE) {
        setHasNextPage(true);
        setPublicGames(data.slice(0, ITEMS_PER_PAGE));
      } else {
        setHasNextPage(false);
        setPublicGames(data);
      }
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "An unexpected error occurred.";
      console.error("Error fetching public games:", error);
      setError(message);
      setPublicGames([]);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, selectedDate]);

  useEffect(() => {
    fetchPublicGames();
  }, [fetchPublicGames]);

  const handleRequestToJoin = async (gameId: number) => {
    if (!accessToken || !currentUser) {
        toast.error("You must be logged in to request to join a game.");
        return;
    }
    setJoinRequestLoading(prev => ({ ...prev, [gameId]: true }));
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/games/${gameId}/join`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${accessToken}` },
        });
        const data = await response.json();
        if (!response.ok) {
            const errorMessage = typeof data.detail === 'string' ? data.detail : "Failed to send join request.";
            throw new Error(errorMessage);
        }
        toast.success("Join request sent successfully! The game creator will be notified.");
        fetchPublicGames();
    } catch (error: unknown) {
        const message = error instanceof Error ? error.message : "Failed to send join request.";
        console.error("Error sending join request:", error);
        toast.error(message);
    } finally {
        setJoinRequestLoading(prev => ({ ...prev, [gameId]: false }));
    }
  };

  const getAvailableSlots = (game: PublicGame): number => {
    const acceptedPlayers = game.players.filter(p => p.status.toUpperCase() === 'ACCEPTED').length;
    return MAX_PLAYERS_PER_GAME - acceptedPlayers;
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 space-y-6">
      <header className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Discover Public Games</h1>
        <p className="text-muted-foreground">Find open Padel games and request to join.</p>
      </header>

      <div className="flex flex-col sm:flex-row gap-4 mb-6 p-4 border rounded-lg items-center">
        <Label htmlFor="date-filter" className="mb-1 sm:mb-0 sm:mr-2 whitespace-nowrap">Filter by Date:</Label>
        <Popover>
            <PopoverTrigger asChild>
              <Button
                id="date-filter"
                variant={"outline"}
                className={`w-full sm:w-[260px] justify-start text-left font-normal ${!selectedDate && "text-muted-foreground"}`}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {selectedDate ? format(selectedDate, "PPP") : <span>Pick a date</span>}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={(date) => { setSelectedDate(date); setCurrentPage(1); }}
                initialFocus
              />
            </PopoverContent>
        </Popover>
        {selectedDate && (
            <Button variant="ghost" onClick={() => { setSelectedDate(undefined); setCurrentPage(1); }} className="text-sm">Clear Date</Button>
        )}
      </div>

      {isLoading && (
        <div className="flex justify-center items-center py-10">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
          <p className="ml-3 text-muted-foreground">Loading public games...</p>
        </div>
      )}

      {error && (
        <div className="flex flex-col items-center justify-center py-10 bg-destructive/10 p-4 rounded-md">
          <AlertTriangle className="h-10 w-10 text-destructive mb-2" />
          <p className="text-destructive font-semibold">Error loading games</p>
          <p className="text-sm text-muted-foreground">{error}</p>
          <Button variant="outline" onClick={fetchPublicGames} className="mt-4">Try Again</Button>
        </div>
      )}

      {!isLoading && !error && publicGames.length === 0 && (
        <div className="text-center py-10">
          <p className="text-xl text-muted-foreground">No public games found matching your criteria.</p>
          {selectedDate && <p className="text-sm">Try clearing the date filter or checking another day.</p>}
        </div>
      )}

      {!isLoading && !error && publicGames.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {publicGames.map((game) => {
            const availableSlots = getAvailableSlots(game);
            const isCurrentUserCreator = game.booking.user_id === currentUser?.id;
            const isCurrentUserInGame = game.players.some(p => p.user.id === currentUser?.id);
            const canRequestToJoin = availableSlots > 0 && !isCurrentUserCreator && !isCurrentUserInGame;

            return (
              <Card key={game.id} className="flex flex-col">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">{game.booking.court?.club?.name || 'Club Details Missing'}</CardTitle>
                    <Badge variant="secondary">{game.skill_level || 'Any Skill'}</Badge>
                  </div>
                  <CardDescription>
                    {game.booking.court?.name || `Court ID: ${game.booking.court_id}`} at {format(parseISO(game.booking.start_time), 'HH:mm')} - {format(parseISO(game.booking.end_time), 'HH:mm')}
                    <br/>On {format(parseISO(game.booking.start_time), 'PPP (EEEE)')}
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-grow space-y-2">
                    <p className="text-sm flex items-center">
                        <Users className="mr-2 h-4 w-4 text-muted-foreground" /> 
                        {MAX_PLAYERS_PER_GAME - availableSlots} / {MAX_PLAYERS_PER_GAME} players joined. 
                        <span className={availableSlots > 0 ? 'text-green-600 ml-1 font-semibold' : 'text-red-600 ml-1 font-semibold'}>
                            ({availableSlots > 0 ? `${availableSlots} slot${availableSlots > 1 ? 's' : ''} open` : 'Full'})
                        </span>
                    </p>
                    {/* TODO: Display list of accepted players if desired */}
                </CardContent>
                <CardFooter>
                  {canRequestToJoin ? (
                    <Button 
                        className="w-full" 
                        onClick={() => handleRequestToJoin(game.id)} 
                        disabled={joinRequestLoading[game.id]}
                    >
                        {joinRequestLoading[game.id] ? <Loader2 className="mr-2 h-4 w-4 animate-spin"/> : <UserPlus className="mr-2 h-4 w-4" />}
                        Request to Join
                    </Button>
                  ) : (
                    <Button className="w-full" disabled variant="outline">
                        {isCurrentUserInGame ? "You're in this game" : (isCurrentUserCreator ? "Your Game" : "Game Full / Cannot Join")}
                    </Button>
                  )}
                  <Link href={`/games/${game.id}`} passHref legacyBehavior>
                    <Button variant="ghost" size="sm" className="mt-2 w-full">View Game Details</Button>
                  </Link>
                </CardFooter>
              </Card>
            );
        })}
        </div>
      )}

      {!isLoading && !error && (publicGames.length > 0 || currentPage > 1) && (
        <div className="flex justify-center items-center space-x-4 mt-8">
          <Button variant="outline" onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))} disabled={currentPage === 1 || isLoading}>Previous</Button>
          <span className="text-sm text-muted-foreground">Page {currentPage}</span>
          <Button variant="outline" onClick={() => setCurrentPage(prev => prev + 1)} disabled={!hasNextPage || isLoading}>Next</Button>
        </div>
      )}
    </div>
  );
}

const PublicGamesDiscoveryPage = () => (
    <Suspense fallback={<div className="flex justify-center items-center min-h-screen"><Loader2 className="h-12 w-12 animate-spin" /></div>}>
        <PublicGamesPageInternal />
    </Suspense>
);

export default withAuth(PublicGamesDiscoveryPage); // Requires auth to request to join 