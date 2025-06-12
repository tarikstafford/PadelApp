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

const MAX_PLAYERS_PER_GAME = 4; // Define the constant here
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// Interfaces matching backend schemas
interface UserForGame {
    id: number;
    name?: string | null;
    email: string;
    profile_picture_url?: string | null;
}
interface GamePlayer {
    user: UserForGame;
    status: string; // "ACCEPTED", "INVITED", "DECLINED"
}
interface BookingForGame {
    id: number;
    court_id: number;
    user_id: number; // Ensure this is present for creator check
    start_time: string; // ISO string
    end_time: string;   // ISO string
    // Potentially add court and club names if backend enriches this further
    court?: { id: number; name?: string | null, club_id?: number, club?: { id: number; name?: string | null; address?: string | null; city?: string | null; } };
}
interface GameDetail {
    id: number;
    booking: BookingForGame;
    game_type: "PRIVATE" | "PUBLIC";
    skill_level?: string | null;
    players: GamePlayer[];
}

// PlayerSlot Component
const PlayerSlot = ({ player, onInvite }: { player?: GamePlayer, onInvite: () => void }) => {
    if (player) {
        return (
            <div className="flex flex-col items-center space-y-2">
                <div className="relative w-24 h-24">
                    <Image
                        src={player.user.profile_picture_url || `https://avatar.vercel.sh/${player.user.email}?s=96`}
                        alt={player.user.name || player.user.email}
                        layout="fill"
                        className="rounded-full object-cover"
                    />
                </div>
                <span className="text-sm font-medium text-center truncate w-24">{player.user.name || 'Player'}</span>
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

function GameDetailPageInternal() {
  const params = useParams();
  const router = useRouter();
  const { user: currentUser, accessToken } = useAuth(); // Renamed to currentUser for clarity
  const gameId = params.gameId as string;

  const [game, setGame] = useState<GameDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRespondingToInvite, setIsRespondingToInvite] = useState(false);
  const [isManagingPlayer, setIsManagingPlayer] = useState<Record<number, boolean>>({}); // { playerUserId: isLoading }
  const [inviteLink, setInviteLink] = useState('');
  const [isInviteDialogOpen, setIsInviteDialogOpen] = useState(false);

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
        const errorData: { detail?: string } = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to fetch game details");
      }
      const data: GameDetail = await response.json();
      setGame(data);
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
    if (!game || !currentUser || !accessToken || game.booking.user_id !== currentUser.id) {
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

  if (isLoading) { return <div className="flex justify-center items-center min-h-[calc(100vh-200px)]"><Loader2 className="h-16 w-16 animate-spin text-primary" /></div>; }
  if (error) { return <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] text-center px-4"><AlertTriangle className="h-12 w-12 text-destructive mb-3" /><h2 className="text-xl font-semibold text-destructive mb-2">Error loading game details</h2><p className="text-sm text-muted-foreground mb-4">{error}</p><Button variant="outline" onClick={() => router.push('/bookings')}>Back to My Bookings</Button></div>; }
  if (!game) { return <div className="text-center py-10"><p className="text-xl text-muted-foreground">Game not found.</p><Link href="/bookings"><Button variant="link" className="mt-2"><ArrowLeft className="mr-2 h-4 w-4" /> Back to My Bookings</Button></Link></div>; }

  const isCurrentUserGameCreator = currentUser?.id === game.booking.user_id;
  const currentUserGamePlayerInfo = game.players.find(p => p.user.id === currentUser?.id);
  const courtName = game.booking.court?.name || `ID ${game.booking.court_id}`;
  const clubName = game.booking.court?.club?.name || (game.booking.court?.club_id ? `Club ID: ${game.booking.court.club_id}` : 'Club details unavailable');

  const acceptedPlayers = game.players.filter(p => p.status === "ACCEPTED");
  const teamA = [acceptedPlayers[0], acceptedPlayers[1]]; // First two players
  const teamB = [acceptedPlayers[2], acceptedPlayers[3]]; // Next two players

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
                    {game.skill_level && ` - Skill Level: ${game.skill_level}`}
                </CardDescription>
            </div>
            {/* TODO: Add an Edit Game button for game creator */}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
            <div>
                <h3 className="text-lg font-semibold mb-1 flex items-center"><CalendarIcon className="mr-2 h-5 w-5 text-muted-foreground"/> Date & Time</h3>
                <p className="text-sm ml-7">{format(parseISO(game.booking.start_time), 'PPP (EEEE)')}</p>
                <p className="text-sm ml-7">{format(parseISO(game.booking.start_time), 'HH:mm')} - {format(parseISO(game.booking.end_time), 'HH:mm')}</p>
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
                            {game.players.map(playerEntry => (
                                <li key={playerEntry.user.id} className="flex flex-col sm:flex-row justify-between sm:items-center p-3 border rounded-md bg-card hover:bg-muted/50 transition-colors">
                                    <div className="flex items-center space-x-3 mb-2 sm:mb-0">
                                        <div className="relative h-10 w-10">
                                            <Image src={playerEntry.user.profile_picture_url || `https://avatar.vercel.sh/${playerEntry.user.email}?s=40`} alt={playerEntry.user.name || playerEntry.user.email} layout="fill" className="rounded-full" />
                                        </div>
                                        <div>
                                            <p className="font-medium">{playerEntry.user.name || playerEntry.user.email}</p>
                                            <p className="text-xs text-muted-foreground">{playerEntry.user.email}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        {getPlayerStatusIcon(playerEntry.status)}
                                        <Badge variant={getPlayerStatusVariant(playerEntry.status)}>{playerEntry.status}</Badge>
                                        {isCurrentUserGameCreator && playerEntry.status === "REQUESTED_TO_JOIN" && (
                                            <div className="flex space-x-2 ml-2">
                                                <Button size="sm" className="bg-green-600 hover:bg-green-700 text-white px-2 py-1 h-auto text-xs" onClick={() => handleManageJoinRequest(playerEntry.user.id, "ACCEPTED")} disabled={isManagingPlayer[playerEntry.user.id] || game.players.filter(p=>p.status === "ACCEPTED").length >= MAX_PLAYERS_PER_GAME}>
                                                    {isManagingPlayer[playerEntry.user.id] && game.players.filter(p=>p.status === "ACCEPTED").length < MAX_PLAYERS_PER_GAME ? <Loader2 className="h-3 w-3 animate-spin"/> : <CheckCircleIcon className="h-3 w-3"/>} Approve
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
    </div>
  );
}

const GameDetailPage = () => (
    <Suspense fallback={<div className="flex justify-center items-center min-h-screen"><Loader2 className="h-12 w-12 animate-spin" /></div>}>
        <GameDetailPageInternal />
    </Suspense>
);

export default withAuth(GameDetailPage); 