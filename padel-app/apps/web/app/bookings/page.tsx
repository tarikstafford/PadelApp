"use client";

import React, { useState, useEffect, useCallback, Suspense } from 'react';
import Link from 'next/link';
// import { useRouter } from 'next/navigation'; // Unused
import { Button } from "@workspace/ui/components/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@workspace/ui/components/card"; // Removed unused CardFooter
import { Calendar } from "@workspace/ui/components/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@workspace/ui/components/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@workspace/ui/components/select";
import { Badge } from "@workspace/ui/components/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@workspace/ui/components/avatar";
import { Loader2, AlertTriangle, CalendarIcon, Users, Disc2 } from 'lucide-react'; // Removed unused ArrowLeft
import { useAuth } from '@/contexts/AuthContext';
// import { toast } from 'sonner'; // Unused
import withAuth from '@/components/auth/withAuth';
import { format, parseISO } from 'date-fns'; // Removed unused addDays
import type { DateRange } from "react-day-picker";

// Sub-interfaces for nested data structures
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
  }
}

interface Game {
  id: number;
  game_type: 'PUBLIC' | 'PRIVATE';
  players: GamePlayer[];
}

// Updated Booking interface
interface Booking {
  id: number;
  court_id: number;
  user_id: number;
  start_time: string; // ISO string
  end_time: string;   // ISO string
  status: string; // e.g., "CONFIRMED", "CANCELLED", "COMPLETED"
  court: Court;
  game: Game | null;
}

const ITEMS_PER_PAGE = 10;
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

function BookingsPageInternal() {
  const { accessToken } = useAuth();
  // const router = useRouter(); // Unused

  const [bookings, setBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [currentPage, setCurrentPage] = useState(1);
  const [hasNextPage, setHasNextPage] = useState(false);

  const [dateRange, setDateRange] = useState<DateRange | undefined>(undefined);
  const [sortBy, setSortBy] = useState("start_time");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const fetchUserBookings = useCallback(async () => {
    if (!accessToken) return;

    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.append('skip', ((currentPage - 1) * ITEMS_PER_PAGE).toString());
      params.append('limit', (ITEMS_PER_PAGE + 1).toString());
      if (dateRange?.from) params.append('start_date_filter', format(dateRange.from, 'yyyy-MM-dd'));
      if (dateRange?.to) params.append('end_date_filter', format(dateRange.to, 'yyyy-MM-dd'));
      if (sortBy) params.append('sort_by', sortBy);
      if (sortOrder === 'desc') params.append('sort_desc', 'true');

      const response = await fetch(`${API_BASE_URL}/api/v1/bookings?${params.toString()}`, {
        headers: { 'Authorization': `Bearer ${accessToken}` },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to fetch bookings" }));
        const errorMessage = typeof errorData.detail === 'string' ? errorData.detail : "Failed to fetch bookings";
        throw new Error(errorMessage);
      }
      const data: Booking[] = await response.json();
      
      if (data.length > ITEMS_PER_PAGE) {
        setHasNextPage(true);
        setBookings(data.slice(0, ITEMS_PER_PAGE));
      } else {
        setHasNextPage(false);
        setBookings(data);
      }
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "An unexpected error occurred.";
      console.error("Error fetching bookings:", error);
      setError(message);
      setBookings([]);
    } finally {
      setIsLoading(false);
    }
  }, [accessToken, currentPage, dateRange, sortBy, sortOrder]);

  useEffect(() => {
    fetchUserBookings();
  }, [fetchUserBookings]);

  const handleSortChange = (value: string) => {
    const [field, order] = value.split('-');
    setSortBy(field || "start_time");
    setSortOrder((order || "desc") as "asc" | "desc");
    setCurrentPage(1);
  };

  const getStatusVariant = (status: string): "default" | "outline" | "destructive" | "secondary" => {
    switch (status.toUpperCase()) {
      case 'CONFIRMED':
      case 'UPCOMING':
        return "default";
      case 'COMPLETED':
        return "secondary";
      case 'CANCELLED':
        return "destructive";
      default:
        return "outline";
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-6">
      <header className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">My Bookings</h1>
        <p className="text-muted-foreground">View and manage your Padel court reservations.</p>
      </header>

      {/* Filters and Sort */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 p-4 border rounded-lg items-end">
        <div>
          <label htmlFor="dateRange" className="text-sm font-medium mb-1 block">Filter by Date Range</label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                id="dateRange"
                variant={"outline"}
                className={`w-full justify-start text-left font-normal ${!dateRange && "text-muted-foreground"}`}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {dateRange?.from ? (
                  dateRange.to ? (
                    <>{format(dateRange.from, "LLL dd, y")} - {format(dateRange.to, "LLL dd, y")}</>
                  ) : (
                    format(dateRange.from, "LLL dd, y")
                  )
                ) : (
                  <span>Pick a date range</span>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                initialFocus
                mode="range"
                defaultMonth={dateRange?.from}
                selected={dateRange}
                onSelect={(range) => { setDateRange(range); setCurrentPage(1); }}
                numberOfMonths={2}
              />
            </PopoverContent>
          </Popover>
        </div>
        <div>
          <label htmlFor="sortByBookings" className="text-sm font-medium mb-1 block">Sort by</label>
          <Select 
            value={`${sortBy}-${sortOrder}`}
            onValueChange={handleSortChange}
          >
            <SelectTrigger id="sortByBookings">
              <SelectValue placeholder="Sort by..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="start_time-desc">Date (Newest First)</SelectItem>
              <SelectItem value="start_time-asc">Date (Oldest First)</SelectItem>
              <SelectItem value="status-asc">Status (A-Z)</SelectItem>
              <SelectItem value="status-desc">Status (Z-A)</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {isLoading && (
        <div className="flex justify-center items-center py-10">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
          <p className="ml-3 text-muted-foreground">Loading your bookings...</p>
        </div>
      )}

      {error && (
        <div className="flex flex-col items-center justify-center py-10 bg-destructive/10 p-4 rounded-md">
          <AlertTriangle className="h-10 w-10 text-destructive mb-2" />
          <p className="text-destructive font-semibold">Error loading bookings</p>
          <p className="text-sm text-muted-foreground">{error}</p>
          <Button variant="outline" onClick={fetchUserBookings} className="mt-4">Try Again</Button>
        </div>
      )}

      {!isLoading && !error && bookings.length === 0 && (
        <div className="text-center py-10">
          <p className="text-xl text-muted-foreground">You have no bookings yet.</p>
          <Link href="/discover">
            <Button className="mt-4">Find a Court to Book</Button>
          </Link>
        </div>
      )}

      {!isLoading && !error && bookings.length > 0 && (
        <div className="space-y-4">
          {bookings.map((booking) => (
            <Card key={booking.id} className="transition-shadow flex flex-col">
              <Link href={`/bookings/${booking.id}`} passHref legacyBehavior>
                <div className="cursor-pointer hover:bg-muted/50 rounded-t-lg">
                <CardHeader>
                    <CardTitle className="flex items-center">
                      <Disc2 className="mr-2 h-5 w-5 text-primary" />
                      {booking.court?.club?.name} - {booking.court?.name}
                    </CardTitle>
                  <CardDescription>
                      Booked for: {format(parseISO(booking.start_time), 'PPP, HH:mm')} - {format(parseISO(booking.end_time), 'HH:mm')}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Badge variant={getStatusVariant(booking.status)}>{booking.status}</Badge>

                  {/* Display players if a game exists */}
                  {booking.game && booking.game.players.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-sm font-medium text-muted-foreground mb-2 flex items-center">
                        <Users className="mr-2 h-4 w-4" /> Players in Game
                      </h4>
                      <div className="flex flex-wrap items-center gap-2">
                        {booking.game.players.map((player) => (
                          <div key={player.user_id} className="flex items-center gap-2" title={player.user.full_name}>
                             <Avatar className="h-8 w-8">
                              <AvatarImage src={player.user.profile_picture_url || ''} alt={player.user.full_name} />
                              <AvatarFallback>{player.user.full_name.charAt(0)}</AvatarFallback>
                            </Avatar>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
                </div>
              </Link>
              <CardFooter className="bg-muted/30 border-t pt-4 mt-auto">
                 {booking.game ? (
                    <Link href={`/games/${booking.game.id}`} className="w-full">
                      <Button className="w-full" variant="outline">View Game</Button>
                    </Link>
                  ) : (
                    <Link href={`/book/${booking.court.id}?bookingId=${booking.id}`} className="w-full">
                      <Button className="w-full">Create Game</Button>
                    </Link>
                  )}
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {!isLoading && !error && (bookings.length > 0 || currentPage > 1) && (
        <div className="flex justify-center items-center space-x-4 mt-8">
          <Button 
            variant="outline" 
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))} 
            disabled={currentPage === 1 || isLoading}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">Page {currentPage}</span>
          <Button 
            variant="outline" 
            onClick={() => setCurrentPage(prev => prev + 1)} 
            disabled={!hasNextPage || isLoading}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}

// Wrap the internal component with Suspense (if useSearchParams were used directly here) and withAuth HOC
const UserBookingsPage = () => (
    <Suspense fallback={<div className="flex justify-center items-center min-h-screen"><Loader2 className="h-12 w-12 animate-spin" /></div>}>
        <BookingsPageInternal />
    </Suspense>
);

export default withAuth(UserBookingsPage); 