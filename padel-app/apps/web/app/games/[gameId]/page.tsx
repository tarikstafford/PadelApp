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

// --- Interfaces copied from bookings/page.tsx for consistency ---
interface Club {
  id: number;
  name: string;
}

interface Court {
  id: number;
  name: string;
  club: Club;
}

interface GamePlayer {
  user_id: number;
  status: string;
  user: {
    id: number;
    full_name: string;
    profile_picture_url: string | null;
    email: string;
  };
}

interface Game {
  id: number;
  game_type: 'PUBLIC' | 'PRIVATE';
  players: GamePlayer[];
  booking: Booking;
}

interface Booking {
  id: number;
  court_id: number;
  user_id: number;
  start_time: string;
  end_time: string;
  status: string;
  court: Court;
  game: Game | null;
}

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
      // Defensive normalization for nested court/club/player
      const normalizedGame: Game = {
        id: rawData.id,
        game_type: rawData.game_type,
        players: (rawData.players || []).map((p: any) => ({
          user_id: p.user?.id ?? p.user_id,
          status: p.status,
          user: {
            id: p.user?.id ?? p.user_id,
            full_name: p.user?.full_name ?? '',
            profile_picture_url: p.user?.profile_picture_url ?? null,
            email: p.user?.email ?? '', // Always include email for fallback
          },
        })),
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

  if (isLoading) { return <div className="flex justify-center items-center min-h-[calc(100vh-200px)]"><Loader2 className="h-16 w-16 animate-spin text-primary" /></div>; }
  if (error) { return <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] text-center px-4"><AlertTriangle className="h-12 w-12 text-destructive mb-3" /><h2 className="text-xl font-semibold text-destructive mb-2">Error loading game details</h2><p className="text-sm text-muted-foreground mb-4">{error}</p><Button variant="outline" onClick={() => router.push('/bookings')}>Back to My Bookings</Button></div>; }
  if (!game) { return <div className="text-center py-10"><p className="text-xl text-muted-foreground">Game not found.</p><Link href="/bookings"><Button variant="link" className="mt-2"><ArrowLeft className="mr-2 h-4 w-4" /> Back to My Bookings</Button></Link></div>; }

  const isCurrentUserGameCreator = (currentUser?.id) === (game.booking?.user_id);
  const currentUserGamePlayerInfo = (game.players ?? []).find(p => p.user_id === currentUser?.id);
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
                            {game.players.map(playerEntry => (
                                <li key={playerEntry.user_id} className="flex flex-col sm:flex-row justify-between sm:items-center p-3 border rounded-md bg-card hover:bg-muted/50 transition-colors">
                                    <div className="flex items-center space-x-3 mb-2 sm:mb-0">
                                        <div className="relative h-10 w-10">
                                            <Image src={playerEntry.user?.profile_picture_url || `/default-avatar.png`} alt={playerEntry.user.full_name} layout="fill" className="rounded-full" />
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
                                                <Button size="sm" className="bg-green-600 hover:bg-green-700 text-white px-2 py-1 h-auto text-xs" onClick={() => handleManageJoinRequest(playerEntry.user_id, "ACCEPTED")} disabled={isManagingPlayer[playerEntry.user_id] || (game.players?.filter(p=>p.status === "ACCEPTED").length ?? 0) >= MAX_PLAYERS_PER_GAME}>
                                                    {isManagingPlayer[playerEntry.user_id] && (game.players?.filter(p=>p.status === "ACCEPTED").length ?? 0) < MAX_PLAYERS_PER_GAME ? <Loader2 className="h-3 w-3 animate-spin"/> : <CheckCircleIcon className="h-3 w-3"/>} Approve
                                                </Button>
                                                <Button variant="destructive" size="sm" className="px-2 py-1 h-auto text-xs" onClick={() => handleManageJoinRequest(playerEntry.user_id, "DECLINED")} disabled={isManagingPlayer[playerEntry.user_id]}>
                                                    {isManagingPlayer[playerEntry.user_id] ? <Loader2 className="h-3 w-3 animate-spin"/> : <XCircleIcon className="h-3 w-3" />} Decline
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