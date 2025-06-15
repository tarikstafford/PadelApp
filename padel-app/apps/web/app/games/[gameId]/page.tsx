"use client";

import React, { useState, useEffect, useCallback, Suspense } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { Button } from "@workspace/ui/components/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@workspace/ui/components/card";
import { Badge } from "@workspace/ui/components/badge";
import { Loader2, AlertTriangle, ArrowLeft, Calendar as CalendarIcon, Users, Hash, ShieldCheck, UserCheck, UserX, Info, CheckCircleIcon, XCircleIcon, UserPlus, Copy } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import withAuth from '@/components/auth/withAuth';
import { format, parseISO } from 'date-fns';
import { toast } from 'sonner';
import { Separator } from '@workspace/ui/components/separator';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@workspace/ui/components/dialog';
import { Input } from '@workspace/ui/components/input';
import { Label } from '@workspace/ui/components/label';
import { Avatar, AvatarFallback, AvatarImage } from "@workspace/ui/components/avatar";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@workspace/ui/components/tooltip";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@workspace/ui/components/alert-dialog";
import { apiClient } from "@/lib/api";
import { Game, GamePlayer, Booking } from "@/lib/types";

const MAX_PLAYERS_PER_GAME = 4; // Define the constant here
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// PlayerSlot Component
const PlayerSlot = ({ player, onInvite }: { player?: GamePlayer, onInvite: () => void }) => {
    if (player) {
        return (
            <div className="flex flex-col items-center space-y-2">
                <div className="relative w-24 h-24">
                    <Image
                        src={player.user?.profile_picture_url || (player.user?.email ? `https://avatar.vercel.sh/${player.user.email}?s=96` : "/default-avatar.png")}
                        alt={player.user?.full_name || player.user?.email || "Unknown User"}
                        layout="fill"
                        className="rounded-full object-cover"
                    />
                </div>
                <span className="text-sm font-medium text-center truncate w-24">{player.user?.full_name || player.user?.email || 'Unknown'}</span>
            </div>
        );
    }
    return (
        <div className="flex flex-col items-center space-y-2">
            <button onClick={onInvite} className="w-24 h-24 rounded-full bg-muted flex items-center justify-center text-sm text-muted-foreground hover:bg-muted/80 transition-colors">
                <UserPlus className="h-8 w-8 text-muted-foreground/50" />
            </button>
            <span className="text-sm text-muted-foreground">Invite Player</span>
        </div>
    );
};

// Interfaces are now imported from @/lib/types

function GameDetailPageInternal() {
  const params = useParams();
  const router = useRouter();
  const { user: currentUser, accessToken } = useAuth(); // Renamed to currentUser for clarity
  const gameId = params.gameId as string;

  const [game, setGame] = useState<Game | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRespondingToInvite, setIsRespondingToInvite] = useState(false);
  const [isManagingPlayer, setIsManagingPlayer] = useState<Record<number, boolean>>({}); // { playerUserId: isLoading }
  const [inviteLink, setInviteLink] = useState('');
  const [isInviteDialogOpen, setIsInviteDialogOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const generateInviteLink = () => {
    const link = `${window.location.origin}/games/${gameId}`;
    setInviteLink(link);
    setIsInviteDialogOpen(true);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(inviteLink);
    toast.success("Invitation link copied to clipboard!");
  };

  const fetchGameData = useCallback(async () => {
    if (!gameId || !accessToken) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/games/${gameId}`, {
        headers: { 'Authorization': `Bearer ${accessToken}` },
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to fetch game details");
      }
      // Normalize the data to match the interfaces above
      const rawData = await response.json();
      
      const normalizedPlayers = (rawData.players || []).map((p: GamePlayer) => ({
        status: (p.status || '').toUpperCase(),
        user: p.user || {
            id: 0,
            full_name: 'Unknown Player',
            profile_picture_url: null,
            email: ''
        }
      }));

      const normalizedGame: Game = {
        id: rawData.id,
        game_type: rawData.game_type,
        players: normalizedPlayers,
        booking: {
          id: rawData.booking?.id ?? rawData.booking_id,
          court_id: rawData.booking?.court_id ?? rawData.court_id,
          user_id: rawData.booking?.user_id ?? rawData.user_id,
          start_time: rawData.booking?.start_time ?? rawData.start_time,
          end_time: rawData.booking?.end_time ?? rawData.end_time,
          status: rawData.booking?.status ?? rawData.status ?? 'CONFIRMED',
          court: rawData.booking?.court || {
            id: rawData.booking?.court?.id ?? rawData.court_id ?? 0,
            name: rawData.booking?.court?.name ?? 'Unknown Court',
            club: rawData.booking?.court?.club || {
              id: rawData.booking?.court?.club?.id ?? 0,
              name: rawData.booking?.court?.club?.name ?? 'Unknown Club',
            },
          },
          game: null, // Prevent circular reference
        },
        result_submitted: rawData.result_submitted,
        winning_team_id: rawData.winning_team_id,
        team1: rawData.team1,
        team2: rawData.team2,
      };
      setGame(normalizedGame as Game);
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "An unexpected error occurred.";
      console.error(`Error fetching game ${gameId} details:`, error);
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [gameId, accessToken]);

  useEffect(() => {
    fetchGameData();
  }, [fetchGameData]);

  const handleInvitationResponse = async (newStatus: "ACCEPTED" | "DECLINED") => {
    if (!game || !currentUser || !accessToken) {
        toast.error("Cannot respond to invitation. Missing data or not authenticated.");
        return;
    }
    setIsRespondingToInvite(true);
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/games/${game.id}/invitations/${currentUser.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` },
            body: JSON.stringify({ status: newStatus }),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Failed to update invitation status.");
        }
        toast.success(`Invitation ${newStatus.toLowerCase()} successfully!`);
        fetchGameData();
    } catch (error: unknown) {
        const message = error instanceof Error ? error.message : "Failed to update invitation status.";
        console.error("Error responding to invitation:", error);
        toast.error(message);
    } finally {
        setIsRespondingToInvite(false);
    }
  };

  const handleManageJoinRequest = async (playerUserId: number, newStatus: "ACCEPTED" | "DECLINED") => {
    if (!game || !currentUser || !accessToken || game.booking?.user_id !== currentUser.id) {
        toast.error("Action not allowed or missing data.");
        return;
    }
    setIsManagingPlayer(prev => ({ ...prev, [playerUserId]: true }));
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/games/${game.id}/players/${playerUserId}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` },
            body: JSON.stringify({ status: newStatus }),
        });
        const data = await response.json(); 
        if (!response.ok) {
            throw new Error(data.detail || "Failed to update player status.");
        }
        toast.success(`Player request ${newStatus.toLowerCase()} successfully!`);
        fetchGameData();
    } catch (error: unknown) {
        const message = error instanceof Error ? error.message : "Failed to update player status.";
        console.error("Error managing join request:", error);
        toast.error(message);
    } finally {
        setIsManagingPlayer(prev => ({ ...prev, [playerUserId]: false }));
    }
  };

  const getPlayerStatusVariant = (status: string): "default" | "outline" | "destructive" | "secondary" => {
    switch (status?.toUpperCase()) {
        case "ACCEPTED": return "default";
        case "INVITED": return "outline";
        case "REQUESTED_TO_JOIN": return "outline";
        case "DECLINED": return "destructive";
        default: return "secondary";
    }
  };
  
  const getPlayerStatusIcon = (status: string) => {
    switch (status?.toUpperCase()) {
        case "ACCEPTED": return <UserCheck className="h-4 w-4 text-green-600" />;
        case "INVITED": return <Info className="h-4 w-4 text-blue-600" />;
        case "REQUESTED_TO_JOIN": return <Info className="h-4 w-4 text-orange-500" />;
        case "DECLINED": return <UserX className="h-4 w-4 text-red-600" />;
        default: return null;
    }
  };

  const handleSubmitResult = async (winningTeamId: number) => {
    setSubmitting(true);
    try {
      await apiClient.post(`/games/${gameId}/result`, { winning_team_id: winningTeamId });
      toast.success("Game result submitted successfully!");
      fetchGameData();
    } catch (error) {
      console.error("Failed to submit game result", error);
      toast.error("Failed to submit game result. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (isLoading) { return <div className="flex justify-center items-center min-h-[calc(100vh-200px)]"><Loader2 className="h-16 w-16 animate-spin text-primary" /></div>; }
  if (error) { return <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] text-center px-4"><AlertTriangle className="h-12 w-12 text-destructive mb-3" /><h2 className="text-xl font-semibold text-destructive mb-2">Error loading game details</h2><p className="text-sm text-muted-foreground mb-4">{error}</p><Button variant="outline" onClick={() => router.push('/bookings')}>Back to My Bookings</Button></div>; }
  if (!game) { return <div className="text-center py-10"><p className="text-xl text-muted-foreground">Game not found.</p><Link href="/bookings"><Button variant="link" className="mt-2"><ArrowLeft className="mr-2 h-4 w-4" /> Back to My Bookings</Button></Link></div>; }

  const isCurrentUserGameCreator = (currentUser?.id) === (game.booking?.user_id);
  const currentUserGamePlayerInfo = (game.players ?? []).find((p: GamePlayer) => p.user.id === currentUser?.id);
  const courtName = game.booking?.court?.name || (game.booking?.court?.id ? `Court ID: ${game.booking.court.id}` : (game.booking ? `Court ID: ${game.booking.court_id}` : 'Court unavailable'));
  const clubName = game.booking?.court?.club?.name || (game.booking?.court?.club?.id ? `Club ID: ${game.booking.court.club.id}` : 'Club details unavailable');

  // Always show 4 slots: fill with accepted players, then null for invite
  const acceptedPlayers = (game.players ?? []).filter(p => p.status === "ACCEPTED");
  const playerSlots: (GamePlayer | undefined)[] = [
    acceptedPlayers[0],
    acceptedPlayers[1],
    acceptedPlayers[2],
    acceptedPlayers[3],
  ];
  const teamA = [playerSlots[0], playerSlots[1]];
  const teamB = [playerSlots[2], playerSlots[3]];

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 space-y-6">
      <Button variant="outline" size="sm" onClick={() => router.back()} className="mb-4">
        <ArrowLeft className="mr-2 h-4 w-4" /> Back
      </Button>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
                <CardTitle className="text-2xl md:text-3xl font-bold">Game Details (ID: {game.id})</CardTitle>
                <CardDescription>
                    {game.game_type === 'PUBLIC' ? <Users className="inline mr-1 h-4 w-4 text-muted-foreground"/> : <ShieldCheck className="inline mr-1 h-4 w-4 text-muted-foreground"/>} 
                    {game.game_type.charAt(0) + game.game_type.slice(1).toLowerCase()} Game
                </CardDescription>
            </div>
            {/* TODO: Add an Edit Game button for game creator */}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
            <div>
                <h3 className="text-lg font-semibold mb-1 flex items-center"><CalendarIcon className="mr-2 h-5 w-5 text-muted-foreground"/> Date & Time</h3>
                <p className="text-sm ml-7">{game.booking?.start_time
                  ? format(parseISO(game.booking.start_time), 'PPP (EEEE)')
                  : "Start time unavailable"}</p>
                <p className="text-sm ml-7">{game.booking?.start_time && game.booking?.end_time
                  ? `${format(parseISO(game.booking.start_time), 'HH:mm')} - ${format(parseISO(game.booking.end_time), 'HH:mm')}`
                  : "Time unavailable"}</p>
            </div>
            <Separator />
            <div>
                <h3 className="text-lg font-semibold mb-2 flex items-center"><Hash className="mr-2 h-5 w-5 text-muted-foreground"/> Court & Club</h3>
                <p className="text-sm ml-7">Court: {courtName}</p>
                <p className="text-sm ml-7">Club: {clubName}</p>
            </div>
            <Separator />
            <div>
                <h3 className="text-lg font-semibold mb-4 flex items-center"><Users className="mr-2 h-5 w-5 text-muted-foreground"/> Players ({game.players.filter(p => p.status === "ACCEPTED").length} / {MAX_PLAYERS_PER_GAME} Accepted)</h3>
                
                {/* 2v2 Player Display Layout */}
                <div className="flex items-center justify-around p-4 rounded-lg bg-muted/30">
                    {/* Team A */}
                    <div className="flex flex-col items-center space-y-4">
                        <PlayerSlot player={teamA[0]} onInvite={generateInviteLink} />
                        <PlayerSlot player={teamA[1]} onInvite={generateInviteLink} />
                    </div>

                    <div className="text-2xl font-bold text-muted-foreground">VS</div>

                    {/* Team B */}
                    <div className="flex flex-col items-center space-y-4">
                        <PlayerSlot player={teamB[0]} onInvite={generateInviteLink} />
                        <PlayerSlot player={teamB[1]} onInvite={generateInviteLink} />
                    </div>
                </div>

                {/* Player Management List (for invites, requests, etc.) */}
                {game.players.length > 0 && (
                    <div className="mt-6">
                        <h4 className="text-md font-semibold mb-2">Player Management</h4>
                        <ul className="space-y-2">
                            {game.players.map((playerEntry: GamePlayer) => (
                                <li key={playerEntry.user.id} className="flex flex-col sm:flex-row justify-between sm:items-center p-3 border rounded-md bg-card hover:bg-muted/50 transition-colors">
                                    <div className="flex items-center space-x-3 mb-2 sm:mb-0">
                                        <div className="relative h-10 w-10">
                                            <Image src={playerEntry.user.profile_picture_url || `/default-avatar.png`} alt={playerEntry.user.full_name} layout="fill" className="rounded-full" />
                                        </div>
                                        <div>
                                            <p className="font-medium">{playerEntry.user.full_name || playerEntry.user.email || 'Unknown'}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        {getPlayerStatusIcon(playerEntry.status)}
                                        <Badge variant={getPlayerStatusVariant(playerEntry.status)}>{playerEntry.status}</Badge>
                                        {isCurrentUserGameCreator && playerEntry.status === "REQUESTED_TO_JOIN" && (
                                            <div className="flex space-x-2 ml-2">
                                                <Button size="sm" className="bg-green-600 hover:bg-green-700 text-white px-2 py-1 h-auto text-xs" onClick={() => handleManageJoinRequest(playerEntry.user.id, "ACCEPTED")} disabled={isManagingPlayer[playerEntry.user.id] || game.players.filter((p: GamePlayer) => p.status === 'ACCEPTED').length >= MAX_PLAYERS_PER_GAME}>
                                                    {isManagingPlayer[playerEntry.user.id] && (game.players.filter((p: GamePlayer) => p.status === 'ACCEPTED').length) < MAX_PLAYERS_PER_GAME ? <Loader2 className="h-3 w-3 animate-spin"/> : <CheckCircleIcon className="h-3 w-3"/>} Approve
                                                </Button>
                                                <Button variant="destructive" size="sm" className="px-2 py-1 h-auto text-xs" onClick={() => handleManageJoinRequest(playerEntry.user.id, "DECLINED")} disabled={isManagingPlayer[playerEntry.user.id]}>
                                                    {isManagingPlayer[playerEntry.user.id] ? <Loader2 className="h-3 w-3 animate-spin"/> : <XCircleIcon className="h-3 w-3" />} Decline
                                                </Button>
                                            </div>
                                        )}
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            {currentUserGamePlayerInfo && currentUserGamePlayerInfo.status === "INVITED" && (
                <div className="mt-6 pt-4 border-t">
                    <h3 className="text-lg font-semibold mb-3">Your Invitation</h3>
                    <p className="text-sm mb-3">You have been invited to this game. What would you like to do?</p>
                    <div className="flex space-x-3">
                        <Button 
                            onClick={() => handleInvitationResponse("ACCEPTED")} 
                            disabled={isRespondingToInvite}
                            className="bg-green-600 hover:bg-green-700 text-white"
                        >
                            {isRespondingToInvite ? <Loader2 className="mr-2 h-4 w-4 animate-spin"/> : <UserCheck className="mr-2 h-4 w-4" />} Accept
                        </Button>
                        <Button 
                            variant="destructive" 
                            onClick={() => handleInvitationResponse("DECLINED")} 
                            disabled={isRespondingToInvite}
                        >
                            {isRespondingToInvite ? <Loader2 className="mr-2 h-4 w-4 animate-spin"/> : <UserX className="mr-2 h-4 w-4" />} Decline
                        </Button>
                    </div>
                </div>
            )}
        </CardContent>
      </Card>
      
      <Dialog open={isInviteDialogOpen} onOpenChange={setIsInviteDialogOpen}>
        <DialogContent>
            <DialogHeader>
                <DialogTitle>Invite a Player</DialogTitle>
                <DialogDescription>
                    Share this link with someone to invite them to join your game.
                </DialogDescription>
            </DialogHeader>
            <div className="flex items-center space-x-2 mt-4">
                <div className="grid flex-1 gap-2">
                    <Label htmlFor="link" className="sr-only">
                        Link
                    </Label>
                    <Input id="link" value={inviteLink} readOnly />
                </div>
                <Button type="submit" size="sm" className="px-3" onClick={copyToClipboard}>
                    <span className="sr-only">Copy</span>
                    <Copy className="h-4 w-4" />
                </Button>
            </div>
        </DialogContent>
      </Dialog>

      {!game.result_submitted && (
        <div className="mt-8">
          <h2 className="text-xl font-bold mb-4">Submit Result</h2>
          <div className="flex space-x-4">
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button disabled={submitting}>Team 1 Won</Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This action cannot be undone. This will permanently submit the game result and update player ELO ratings.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={() => handleSubmitResult(game.team1!.id)}>Continue</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button disabled={submitting}>Team 2 Won</Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This action cannot be undone. This will permanently submit the game result and update player ELO ratings.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={() => handleSubmitResult(game.team2!.id)}>Continue</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>
      )}

      {game.result_submitted && (
        <div className="mt-8">
          <h2 className="text-xl font-bold mb-4">Result Submitted</h2>
          <p>Winning Team: {game.winning_team_id === game.team1?.id ? 'Team 1' : 'Team 2'}</p>
        </div>
      )}
    </div>
  );
}

const GameDetailPage = () => (
    <Suspense fallback={<div className="flex justify-center items-center min-h-screen"><Loader2 className="h-12 w-12 animate-spin" /></div>}>
        <GameDetailPageInternal />
    </Suspense>
);

export default withAuth(GameDetailPage); 