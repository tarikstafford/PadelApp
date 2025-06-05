"use client";

import React, { useState, useEffect, useCallback, Suspense } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from "@workspace/ui/components/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@workspace/ui/components/card";
import { Calendar } from "@workspace/ui/components/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@workspace/ui/components/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@workspace/ui/components/select";
import { Badge } from "@workspace/ui/components/badge";
import { Loader2, AlertTriangle, CalendarIcon, ArrowLeft } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import withAuth from '@/components/auth/withAuth';
import { format, parseISO, addDays } from 'date-fns';
import type { DateRange } from "react-day-picker";

// Interface for Booking data, assuming backend might enrich this later
// For now, it matches schemas.Booking directly. We might need to fetch court/club names separately per booking if not.
interface Booking {
  id: number;
  court_id: number;
  user_id: number;
  start_time: string; // ISO string
  end_time: string;   // ISO string
  status: string; // e.g., "CONFIRMED", "CANCELLED", "COMPLETED"
  // Anticipated enriched fields (backend would need to provide these or fetch client-side)
  court_name?: string;
  club_name?: string;
}

const ITEMS_PER_PAGE = 10;

function BookingsPageInternal() {
  const { accessToken } = useAuth();
  const router = useRouter();

  const [bookings, setBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [currentPage, setCurrentPage] = useState(1);
  const [hasNextPage, setHasNextPage] = useState(false);

  const [dateRange, setDateRange] = useState<DateRange | undefined>(undefined);
  const [sortBy, setSortBy] = useState("start_time");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const fetchUserBookings = useCallback(async () => {
    if (!accessToken) return; // Should be handled by withAuth, but good check

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

      const response = await fetch(`/api/v1/bookings?${params.toString()}`, {
        headers: { 'Authorization': `Bearer ${accessToken}` },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to fetch bookings" }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      const data: Booking[] = await response.json();
      
      if (data.length > ITEMS_PER_PAGE) {
        setHasNextPage(true);
        setBookings(data.slice(0, ITEMS_PER_PAGE));
      } else {
        setHasNextPage(false);
        setBookings(data);
      }
    } catch (err: any) {
      console.error("Error fetching bookings:", err);
      setError(err.message || "An unexpected error occurred.");
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

  const getStatusVariant = (status: string) => {
    switch (status.toUpperCase()) {
      case 'CONFIRMED':
      case 'UPCOMING': // Assuming UPCOMING might be a status
        return "default"; // Or a specific success-like variant
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
            <Link key={booking.id} href={`/bookings/${booking.id}`} passHref legacyBehavior>
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader>
                  {/* Assuming booking object will have court and club names, if not, fetch or adjust */}
                  <CardTitle>Court ID: {booking.court_id} {/* Placeholder for Court Name */}</CardTitle>
                  <CardDescription>
                    {/* Placeholder for Club Name */} Booked for: {format(parseISO(booking.start_time), 'PPP, HH:mm')} - {format(parseISO(booking.end_time), 'HH:mm')}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Badge variant={getStatusVariant(booking.status)}>{booking.status}</Badge>
                </CardContent>
                 {/* <CardFooter>
                   <Button variant="outline" size="sm">View Details</Button>
                 </CardFooter> */}
              </Card>
            </Link>
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