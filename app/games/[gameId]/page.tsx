"use client";

import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import { useAuth } from '@/components/auth/AuthContext';
import withAuth from '@/components/auth/withAuth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Game, GamePlayer, GameType, GamePlayerStatus } from '@/lib/types/types';
import { getGameDetails, joinGame, leaveGame, respondToGameInvite } from '@/lib/api';
import { toast } from 'sonner';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, UserCheck, UserPlus, LogOut, Check, X } from 'lucide-react';
import { format } from 'date-fns';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

const GameDetailPageInternal = () => {
  const { gameId } = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const [game, setGame] = useState<Game | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const parsedGameId = Array.isArray(gameId) ? gameId[0] : gameId;

  const fetchGameDetails = useCallback(async () => {
    if (!parsedGameId) {
      setError("Game ID is missing.");
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      const gameData = await getGameDetails(parsedGameId);
      setGame(gameData);
    } catch (err: any) {
      setError(err.message || "Failed to fetch game details.");
      toast.error(err.message || "An error occurred.");
    } finally {
      setLoading(false);
    }
  }, [parsedGameId]);

  useEffect(() => {
    fetchGameDetails();
  }, [fetchGameDetails]);

  const handleJoinGame = async () => {
    if (!parsedGameId) return;
    setIsSubmitting(true);
    try {
      await joinGame(parsedGameId);
      toast.success("Successfully joined the game!");
      fetchGameDetails(); // Refresh game details
    } catch (err: any) {
      toast.error(err.message || "Failed to join game.");
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const handleLeaveGame = async () => {
    if (!parsedGameId) return;
    setIsSubmitting(true);
    try {
      await leaveGame(parsedGameId);
      toast.success("You have left the game.");
      fetchGameDetails(); // Refresh game details
    } catch (err: any) {
      toast.error(err.message || "Failed to leave game.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInviteResponse = async (status: GamePlayerStatus.ACCEPTED | GamePlayerStatus.DECLINED) => {
    if (!parsedGameId) return;
    setIsSubmitting(true);
    try {
      await respondToGameInvite(parsedGameId, status);
      toast.success(`You have ${status === GamePlayerStatus.ACCEPTED ? 'accepted' : 'declined'} the invitation.`);
      fetchGameDetails();
    } catch (err: any) {
      toast.error(err.message || "Failed to respond to invitation.");
    } finally {
      setIsSubmitting(false);
    }
  };


  if (loading) {
    return <GameDetailSkeleton />;
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!game) {
    return (
      <div className="container mx-auto p-4">
        <p>Game not found.</p>
      </div>
    );
  }
  
  const currentUserPlayerEntry = game.players.find(p => p.user.id === user?.id);
  const isPlayerInGame = !!currentUserPlayerEntry;
  const hasAccepted = isPlayerInGame && currentUserPlayerEntry.status === GamePlayerStatus.ACCEPTED;
  const isInvited = isPlayerInGame && currentUserPlayerEntry.status === GamePlayerStatus.INVITED;
  const canJoin = game.players.length < 4 && !isPlayerInGame && game.game_type === GameType.PUBLIC;
  const canLeave = isPlayerInGame;

  const renderGameActions = () => {
    if (isInvited) {
      return (
        <div className="flex space-x-2">
          <Button onClick={() => handleInviteResponse(GamePlayerStatus.ACCEPTED)} disabled={isSubmitting}>
            <Check className="mr-2 h-4 w-4"/> Accept
          </Button>
          <Button variant="destructive" onClick={() => handleInviteResponse(GamePlayerStatus.DECLINED)} disabled={isSubmitting}>
            <X className="mr-2 h-4 w-4"/> Decline
          </Button>
        </div>
      );
    }

    return (
        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
            {canJoin && (
                <Button onClick={handleJoinGame} disabled={isSubmitting}>
                    <UserPlus className="mr-2 h-4 w-4" /> Join Game
                </Button>
            )}
            {canLeave && (
                 <Dialog>
                    <DialogTrigger asChild>
                        <Button variant="destructive" disabled={isSubmitting}>
                            <LogOut className="mr-2 h-4 w-4" /> Leave Game
                        </Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                        <DialogTitle>Are you sure?</DialogTitle>
                        <DialogDescription>
                            Leaving the game will remove you from the player list. If this was a mistake, you might be able to rejoin if a slot is still available.
                        </DialogDescription>
                        </DialogHeader>
                        <DialogFooter>
                            <Button variant="ghost" onClick={() => (document.querySelector('[data-state="open"]') as HTMLElement)?.click()}>Cancel</Button>
                            <Button variant="destructive" onClick={() => {
                                handleLeaveGame();
                                (document.querySelector('[data-state="open"]') as HTMLElement)?.click();
                            }} disabled={isSubmitting}>
                                Yes, Leave Game
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            )}
        </div>
    );
  };
  
  return (
    <div className="container mx-auto p-4 sm:p-6 lg:p-8">
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row justify-between sm:items-start">
            <div>
              <CardTitle className="text-2xl sm:text-3xl font-bold">
                Game Details
              </CardTitle>
              <CardDescription>
                {format(new Date(game.start_time), "EEEE, MMMM d, yyyy 'at' h:mm a")}
              </CardDescription>
            </div>
            <Badge 
              variant={game.game_type === GameType.PUBLIC ? "default" : "secondary"}
              className="mt-2 sm:mt-0"
            >
              {game.game_type}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Players</CardTitle>
                <CardDescription>
                  {game.players.filter(p => p.status === 'accepted').length} / 4 players have joined.
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                  {game.players.length > 0 ? (
                    <ul className="space-y-2">
                      {game.players.map(playerEntry => (
                        <li key={playerEntry.user.id} className="flex flex-col sm:flex-row justify-between sm:items-center p-3 border rounded-md bg-card hover:bg-muted/50 transition-colors">
                            <div className="flex items-center space-x-3 mb-2 sm:mb-0">
                                <div className="relative h-10 w-10">
                                    <Image src={playerEntry.user?.profile_picture_url || `/default-avatar.png`} alt={playerEntry.user.full_name || 'Player'} layout="fill" className="rounded-full" />
                                </div>
                                <div>
                                    <p className="font-semibold">{playerEntry.user.full_name}</p>
                                    <p className="text-sm text-muted-foreground">Elo: {Math.round(playerEntry.user.elo_rating ?? 1000)}</p>
                                </div>
                            </div>
                            <Badge variant={playerEntry.status === 'accepted' ? 'success' : 'outline'} className="self-start sm:self-center">
                                {playerEntry.status}
                            </Badge>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <div className="text-center py-4 text-muted-foreground">
                      <p>No players have joined yet.</p>
                    </div>
                  )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                    <div className="flex justify-between">
                        <span className="font-medium text-muted-foreground">Skill Level:</span>
                        <span className="font-semibold">{game.skill_level || 'Not specified'}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="font-medium text-muted-foreground">Court:</span>
                        <span className="font-semibold">{game.booking.court.name}</span>
                    </div>
                     <div className="flex justify-between">
                        <span className="font-medium text-muted-foreground">Club:</span>
                        <span className="font-semibold">{game.booking.court.club.name}</span>
                    </div>
                </div>
              </CardContent>
            </Card>
          </div>
          <div className="mt-6 flex justify-end">
            {renderGameActions()}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};


const GameDetailSkeleton = () => (
  <div className="container mx-auto p-4 sm:p-6 lg:p-8">
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <Skeleton className="h-8 w-48 mb-2" />
            <Skeleton className="h-5 w-64" />
          </div>
          <Skeleton className="h-6 w-20" />
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-24 mb-2" />
              <Skeleton className="h-5 w-40" />
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {[...Array(3)].map((_, i) => (
                  <li key={i} className="flex items-center justify-between p-3 border rounded-md">
                    <div className="flex items-center space-x-3">
                      <Skeleton className="h-10 w-10 rounded-full" />
                      <div>
                        <Skeleton className="h-5 w-32 mb-1" />
                        <Skeleton className="h-4 w-20" />
                      </div>
                    </div>
                    <Skeleton className="h-6 w-20" />
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-24" />
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <Skeleton className="h-5 w-1/3" />
                <Skeleton className="h-5 w-1/2" />
              </div>
              <div className="flex justify-between">
                <Skeleton className="h-5 w-1/4" />
                <Skeleton className="h-5 w-1/2" />
              </div>
            </CardContent>
          </Card>
        </div>
      </CardContent>
    </Card>
  </div>
);

const GameDetailPage = withAuth(GameDetailPageInternal);
export default GameDetailPage; 