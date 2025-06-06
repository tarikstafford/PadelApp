"use client";

import React, { useState, useEffect, useCallback, Suspense } from 'react';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import { Button } from "@workspace/ui/components/button";
import { Calendar } from "@workspace/ui/components/calendar";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@workspace/ui/components/card";
import { Input } from "@workspace/ui/components/input";
import { Label } from "@workspace/ui/components/label";
import { RadioGroup, RadioGroupItem } from "@workspace/ui/components/radio-group";
import { Badge } from "@workspace/ui/components/badge";
import { Loader2, AlertTriangle, ArrowLeft, Users, ShieldCheck } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import withAuth from '@/components/auth/withAuth';
import { format, parseISO } from 'date-fns';
import UserSearchAndInvite, { UserSearchResult } from '@/components/game/UserSearchAndInvite';

interface TimeSlot {
  start_time: string;
  end_time: string;
  is_available: boolean;
}

interface CourtInfo {
  id: string;
  name?: string | null;
  clubName?: string | null;
}

interface BookingDetail {
    id: number;
    court_id: number;
    user_id: number;
    start_time: string;
    end_time: string;
    status: string;
}

interface GamePlayer {
    user: { id: number; name?: string | null; email: string; };
    status: string;
}

interface GameResponse {
    id: number;
    booking_id: number;
    game_type: "PRIVATE" | "PUBLIC";
    skill_level?: string | null;
    players: GamePlayer[];
}

type GameTypeOption = "PRIVATE" | "PUBLIC";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

function BookingPageInternal() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { accessToken } = useAuth();

  const courtId = params.courtId as string;
  const courtNameParam = searchParams.get('courtName');
  const clubNameParam = searchParams.get('clubName');

  const [courtInfo, setCourtInfo] = useState<CourtInfo | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date());
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [selectedTimeSlot, setSelectedTimeSlot] = useState<TimeSlot | null>(null);
  
  const [isLoadingSlots, setIsLoadingSlots] = useState(false);
  const [errorSlots, setErrorSlots] = useState<string | null>(null);
  const [isBooking, setIsBooking] = useState(false);

  const [createdBookingDetails, setCreatedBookingDetails] = useState<BookingDetail | null>(null);
  const [gameType, setGameType] = useState<GameTypeOption>("PRIVATE");
  const [skillLevel, setSkillLevel] = useState("");
  const [isCreatingGame, setIsCreatingGame] = useState(false);
  const [gameCreationError, setGameCreationError] = useState<string | null>(null);
  const [createdGame, setCreatedGame] = useState<GameResponse | null>(null);

  useEffect(() => {
    if (courtId) {
        setCourtInfo({
            id: courtId,
            name: courtNameParam || `Court ${courtId}`,
            clubName: clubNameParam || 'Selected Club'
        });
    }
  }, [courtId, courtNameParam, clubNameParam]);

  const fetchTimeSlots = useCallback(async () => {
    if (!selectedDate || !courtId) return;
    setIsLoadingSlots(true);
    setErrorSlots(null);
    setSelectedTimeSlot(null);
    try {
      const formattedDate = format(selectedDate, 'yyyy-MM-dd');
      const response = await fetch(`${API_BASE_URL}/api/v1/courts/${courtId}/availability?target_date=${formattedDate}`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to fetch time slots" }));
        const errorMessage = typeof errorData.detail === 'string' ? errorData.detail : "Failed to fetch time slots";
        throw new Error(errorMessage);
      }
      const data: TimeSlot[] = await response.json();
      setTimeSlots(data);
    } catch (error: unknown) {
      console.error("Error fetching time slots:", error);
      const message = error instanceof Error ? error.message : "An unexpected error occurred fetching slots.";
      setErrorSlots(message);
      setTimeSlots([]);
    } finally {
      setIsLoadingSlots(false);
    }
  }, [selectedDate, courtId]);

  useEffect(() => {
    fetchTimeSlots();
  }, [fetchTimeSlots]);

  const handleConfirmBooking = async () => {
    if (!selectedTimeSlot || !courtId || !accessToken) {
      toast.error("Please select a time slot and ensure you are logged in.");
      return;
    }
    setIsBooking(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/bookings`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          court_id: parseInt(courtId, 10),
          start_time: selectedTimeSlot.start_time,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        const errorMessage = typeof data.detail === 'string' ? data.detail : "Booking failed. Please try again.";
        throw new Error(errorMessage);
      }
      toast.success("Booking confirmed! Now set up your game.");
      setCreatedBookingDetails(data as BookingDetail);
      setSelectedTimeSlot(null);
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "An unexpected error occurred during booking.";
      console.error("Booking error:", error);
      toast.error(message);
    } finally {
      setIsBooking(false);
    }
  };

  const fetchGameDetails = useCallback(async (gameIdToFetch: number) => {
    if (!accessToken) return;
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/games/${gameIdToFetch}`, {
            headers: { 'Authorization': `Bearer ${accessToken}` },
        });
        const data = await response.json();
        if (!response.ok) {
            const msg = typeof data.detail === 'string' ? data.detail : "Failed to fetch game details";
            throw new Error(msg);
        }
        setCreatedGame(data as GameResponse);
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Could not refresh game details.";
      console.error("Error fetching game details:", error);
      toast.error(message);
    }
  }, [accessToken]);

  const handleCreateGame = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!createdBookingDetails || !accessToken) {
        toast.error("Booking details not found or not authenticated.");
        return;
    }
    setIsCreatingGame(true);
    setGameCreationError(null);
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/games`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${accessToken}`,
            },
            body: JSON.stringify({
                booking_id: createdBookingDetails.id,
                game_type: gameType.toUpperCase(),
                skill_level: skillLevel || null,
            }),
        });
        const data = await response.json();
        if (!response.ok) {
            console.error("Game creation failed. Server response:", data);
            let errorMessage = "Failed to create game.";
            if (response.status === 422 && data.detail) {
                if (Array.isArray(data.detail)) {
                    errorMessage = data.detail.map((err: { loc: any[]; msg: any; }) => `${err.loc.join(' > ')}: ${err.msg}`).join('; ');
                } else if (typeof data.detail === 'string') {
                    errorMessage = data.detail;
                }
            }
            throw new Error(errorMessage);
        }
        toast.success("Game created successfully! Now invite players.");
        setCreatedGame(data as GameResponse);
        setCreatedBookingDetails(null);
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Failed to create game.";
      console.error("Game creation error:", error);
      toast.error(message);
      setGameCreationError(message);
    } finally {
        setIsCreatingGame(false);
    }
  };
  
  const handlePlayerInvited = (invitedPlayer: UserSearchResult) => {
    if (createdGame) {
        fetchGameDetails(createdGame.id);
    }
  };
  
  if (!courtInfo) {
    return (
        <div className="flex justify-center items-center min-h-[calc(100vh-200px)]">
            <Loader2 className="h-16 w-16 animate-spin text-primary" /> <p className="ml-3">Loading court information...</p>
        </div>
    );
  }

  const getPlayerStatusVariant = (status: string) => {
    switch (status.toUpperCase()) {
        case "ACCEPTED": return "default";
        case "INVITED": return "outline";
        case "DECLINED": return "destructive";
        default: return "secondary";
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 space-y-6">
        <Button variant="outline" size="sm" onClick={() => router.back()} className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" /> Back
        </Button>
        <header className="mb-6">
            <h1 className="text-3xl font-bold tracking-tight">Book Court: {courtInfo.name}</h1>
            {courtInfo.clubName && <p className="text-xl text-muted-foreground">at {courtInfo.clubName}</p>}
        </header>

        {!createdBookingDetails && !createdGame && (
            <>
                <Card>
                    <CardHeader><CardTitle>Select Date</CardTitle></CardHeader>
                    <CardContent className="flex justify-center">
                        <Calendar mode="single" selected={selectedDate} onSelect={setSelectedDate} className="rounded-md border" disabled={(date) => date < new Date(new Date().setDate(new Date().getDate() -1))} />
                    </CardContent>
                </Card>

                {selectedDate && (
                    <Card>
                        <CardHeader><CardTitle>Select Time Slot for {format(selectedDate, 'PPP')}</CardTitle></CardHeader>
                        <CardContent>
                            {isLoadingSlots && <div className="flex justify-center items-center py-6"><Loader2 className="h-8 w-8 animate-spin text-primary" /><p className="ml-2 text-muted-foreground">Loading slots...</p></div>}
                            {errorSlots && <div className="text-center py-6 text-destructive"><AlertTriangle className="mx-auto h-8 w-8 mb-2" /><p>{errorSlots}</p><Button variant="outline" onClick={fetchTimeSlots} className="mt-3">Try Again</Button></div>}
                            {!isLoadingSlots && !errorSlots && timeSlots.length === 0 && <p className="text-center text-muted-foreground py-6">No available slots for this date.</p>}
                            {!isLoadingSlots && !errorSlots && timeSlots.length > 0 && (
                                <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2">
                                    {timeSlots.map((slot) => (
                                        <Button key={slot.start_time} variant={selectedTimeSlot?.start_time === slot.start_time ? "default" : (slot.is_available ? "outline" : "secondary")} disabled={!slot.is_available || isBooking} onClick={() => slot.is_available && setSelectedTimeSlot(slot)} className={`w-full ${!slot.is_available ? 'cursor-not-allowed opacity-50' : ''}`}>{format(parseISO(slot.start_time), 'HH:mm')}</Button>
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                )}

                {selectedTimeSlot && selectedDate && courtInfo && (
                    <Card>
                        <CardHeader><CardTitle>Booking Confirmation</CardTitle></CardHeader>
                        <CardContent className="space-y-3">
                            <p><span className="font-semibold">Club:</span> {courtInfo.clubName}</p>
                            <p><span className="font-semibold">Court:</span> {courtInfo.name}</p>
                            <p><span className="font-semibold">Date:</span> {format(selectedDate, 'PPP')}</p>
                            <p><span className="font-semibold">Time:</span> {format(parseISO(selectedTimeSlot.start_time), 'HH:mm')} - {format(parseISO(selectedTimeSlot.end_time), 'HH:mm')}</p>
                        </CardContent>
                        <CardFooter><Button className="w-full" onClick={handleConfirmBooking} disabled={isBooking}>{isBooking ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Confirming...</> : "Confirm Booking"}</Button></CardFooter>
                    </Card>
                )}
            </>
        )}

        {createdBookingDetails && !createdGame && (
            <Card>
                <CardHeader><CardTitle>Create Your Game</CardTitle><CardDescription>Your booking for {courtInfo.name} at {format(parseISO(createdBookingDetails.start_time), 'PPP, HH:mm')} is confirmed. Now set up your game details.</CardDescription></CardHeader>
                <form onSubmit={handleCreateGame}><CardContent className="space-y-4"><div><Label className="text-base font-medium">Game Type</Label><RadioGroup defaultValue="PRIVATE" value={gameType} onValueChange={(value: GameTypeOption) => setGameType(value)} className="mt-2 flex space-x-4"><div className="flex items-center space-x-2"><RadioGroupItem value="PRIVATE" id="gameTypePrivate" /><Label htmlFor="gameTypePrivate" className="font-normal flex items-center"><ShieldCheck className="mr-2 h-4 w-4 text-muted-foreground"/> Private</Label></div><div className="flex items-center space-x-2"><RadioGroupItem value="PUBLIC" id="gameTypePublic" /><Label htmlFor="gameTypePublic" className="font-normal flex items-center"><Users className="mr-2 h-4 w-4 text-muted-foreground"/> Public</Label></div></RadioGroup><p className="text-xs text-muted-foreground mt-1">Private games are only visible to invited players. Public games can be discovered and joined by other users.</p></div><div><Label htmlFor="skillLevel" className="text-base font-medium">Skill Level (Optional)</Label><Input id="skillLevel" value={skillLevel} onChange={(e) => setSkillLevel(e.target.value)} placeholder="E.g., Beginner, Intermediate, Advanced 3.5+" className="mt-2"/></div>{gameCreationError && <p className="text-sm text-destructive">{gameCreationError}</p>}</CardContent><CardFooter><Button type="submit" className="w-full" disabled={isCreatingGame}>{isCreatingGame ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Creating Game...</> : "Create Game & Invite Players"}</Button></CardFooter></form>
            </Card>
        )}

        {createdGame && (
            <Card>
                <CardHeader><CardTitle>Manage Game: {createdGame.game_type}</CardTitle><CardDescription>Booking ID: {createdGame.booking_id}. Game ID: {createdGame.id}. {createdGame.skill_level && `Skill Level: ${createdGame.skill_level}`}</CardDescription></CardHeader>
                <CardContent className="space-y-6"><div><h4 className="text-md font-semibold mb-2">Current Players ({createdGame.players.length} / 4)</h4>{createdGame.players.length > 0 ? (<ul className="space-y-2">{createdGame.players.map((playerEntry) => (<li key={playerEntry.user.id} className="flex justify-between items-center p-2 border rounded-md"><span>{playerEntry.user.name || playerEntry.user.email}</span><Badge variant={getPlayerStatusVariant(playerEntry.status)}>{playerEntry.status}</Badge></li>))}</ul>) : (<p className="text-sm text-muted-foreground">No players yet (except you, the creator).</p>)}</div>{createdGame.players.length < 4 && (<UserSearchAndInvite gameId={createdGame.id} currentPlayers={createdGame.players} onPlayerInvited={handlePlayerInvited} />)}{createdGame.players.length >= 4 && <p className="text-sm text-green-600 font-medium">This game is now full!</p>}</CardContent>
            </Card>
        )}
    </div>
  );
}

const BookCourtPage = () => (
    <Suspense fallback={<div className="flex justify-center items-center min-h-screen"><Loader2 className="h-12 w-12 animate-spin" /></div>}>
        <BookingPageInternal />
    </Suspense>
);

export default withAuth(BookCourtPage); 