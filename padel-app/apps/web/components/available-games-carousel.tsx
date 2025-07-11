"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent } from "@workspace/ui/components/card";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@workspace/ui/components/carousel";
import { Button } from "@workspace/ui/components/button";
import { Loader2, AlertTriangle } from 'lucide-react';
import { Badge } from '@workspace/ui/components/badge';
import { format } from 'date-fns';
import { apiClient } from '@/lib/api';

// Use the correct, nested interface for a public game
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
    players: GamePlayer[];
}

export function AvailableGamesCarousel() {
  const [games, setGames] = useState<PublicGame[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAvailableGames = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient.get<PublicGame[]>('/games/public?limit=10&future_only=true', undefined, null, false);
      setGames(data);
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "An unexpected error occurred.";
      console.error("Error fetching available games:", error);
      setError(message);
      setGames([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAvailableGames();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-48">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Loading available games...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-48 bg-destructive/10 p-4 rounded-md">
        <AlertTriangle className="h-8 w-8 text-destructive mb-2" />
        <p className="text-destructive font-semibold">Error loading games</p>
        <p className="text-sm text-muted-foreground">{error}</p>
        <Button variant="outline" onClick={fetchAvailableGames} className="mt-4">Try Again</Button>
      </div>
    );
  }

  if (games.length === 0) {
    return (
        <div className="text-center py-4">
            <p className="text-md text-muted-foreground">No public games available to join right now.</p>
        </div>
    );
  }

  const getPlayerCount = (game: PublicGame) => {
    return game.players.filter(p => p.status === 'ACCEPTED').length;
  }

  return (
    <div className="w-full max-w-6xl mx-auto py-8">
        <h2 className="text-2xl font-bold tracking-tight mb-4">Available Games to Join</h2>
        <Carousel
            opts={{
            align: "start",
            loop: games.length > 3,
            }}
            className="w-full"
        >
            <CarouselContent>
            {games.map((game) => (
                <CarouselItem key={game.id} className="md:basis-1/2 lg:basis-1/3">
                <div className="p-1">
                    <Card className="h-full flex flex-col">
                    <CardContent className="flex flex-col items-start gap-4 p-6 flex-grow">
                        <div className="w-full">
                            <div className="flex justify-between items-start">
                                {/* Correctly access the nested club name */}
                                <span className="text-sm font-semibold text-primary">{game.booking?.court?.club?.name || 'Club not found'}</span>
                                <Badge variant={game.game_type === 'PUBLIC' ? 'default' : 'secondary'}>{game.game_type}</Badge>
                            </div>
                            {/* Correctly access the nested city */}
                            <p className="text-xs text-muted-foreground">{game.booking?.court?.club?.city || 'City not found'}</p>
                        </div>
                        
                        <div className="w-full">
                             {/* Correctly access start_time from booking */}
                            {game.booking ? (
                                <>
                                    <p className="font-semibold">{format(new Date(game.booking.start_time), 'EEE, MMM d')}</p>
                                    <p className="text-sm text-muted-foreground">
                                        {format(new Date(game.booking.start_time), 'p')} - {format(new Date(game.booking.end_time), 'p')}
                                    </p>
                                </>
                            ) : (
                                <p className="text-sm text-muted-foreground">Date & Time not available</p>
                            )}
                        </div>

                        <div className="w-full space-y-2">
                           <p className="text-sm">Skill Level: <span className="font-medium">{game.skill_level || 'Any'}</span></p>
                           <p className="text-sm">Players Joined: <span className="font-medium">{getPlayerCount(game)}/4</span></p>
                        </div>

                        <div className="w-full mt-auto">
                            <Link href={`/games/${game.id}`} className="w-full">
                                <Button className="w-full">View Game</Button>
                            </Link>
                        </div>
                    </CardContent>
                    </Card>
                </div>
                </CarouselItem>
            ))}
            </CarouselContent>
            <CarouselPrevious />
            <CarouselNext />
        </Carousel>
    </div>
  );
} 