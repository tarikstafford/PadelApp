"use client";

import React, { useState, useEffect, useCallback, Suspense } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from "@workspace/ui/components/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@workspace/ui/components/card";
import { Badge } from "@workspace/ui/components/badge";
import { Loader2, AlertTriangle, ArrowLeft, Calendar as CalendarIcon, Clock, Hash, MapPin } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import withAuth from '@/components/auth/withAuth';
import { format, parseISO } from 'date-fns';
import { Separator } from '@workspace/ui/components/separator';

// Interface for Booking data from backend
interface BookingDetail {
  id: number;
  court_id: number;
  user_id: number;
  start_time: string; // ISO string
  end_time: string;   // ISO string
  status: string;
  // These would ideally be populated by the backend by joining with court and club tables
  court?: { id: number; name: string; club_id?: number; club?: { id: number; name: string; address?: string; city?: string; } };
}

// Helper function to attempt to fetch related Court and Club details if not present
// This is a temporary client-side workaround. Ideally, backend sends all this.
async function fetchEnrichedBookingDetails(bookingId: string, accessToken: string | null): Promise<BookingDetail | null> {
    if (!accessToken) return null;
    const bookingResponse = await fetch(`/api/v1/bookings/${bookingId}`, {
        headers: { 'Authorization': `Bearer ${accessToken}` },
    });
    if (!bookingResponse.ok) {
        const errorData = await bookingResponse.json().catch(() => null);
        throw new Error(errorData?.detail || "Failed to fetch booking details");
    }
    const booking: BookingDetail = await bookingResponse.json();

    // If court details are not already nested, fetch them
    if (booking.court_id && !booking.court) {
        try {
            // This assumes an endpoint /api/v1/courts/{court_id} exists and returns court with club info
            // For now, we only have /api/v1/clubs/{club_id} which returns club with courts.
            // We might need a new backend endpoint or adjust existing ones for full enrichment.
            // As a placeholder, we'll try to get club info via the existing club detail endpoint if possible.
            // This part is highly dependent on available backend endpoints for enrichment.
            // Let's assume for now schemas.Booking on backend is enhanced to include court.name and court.club.name
            // If not, the UI will show Court ID and Club ID.
        } catch (e) {
            console.warn("Could not enrich booking with full court/club details:", e);
        }
    }
    return booking;
}

function BookingDetailPageInternal() {
  const params = useParams();
  const router = useRouter();
  const { accessToken } = useAuth();
  const bookingId = params.bookingId as string;

  const [booking, setBooking] = useState<BookingDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBooking = useCallback(async () => {
    if (!bookingId || !accessToken) return;
    setIsLoading(true);
    setError(null);
    try {
      // Using the helper for potential enrichment, though ideally backend sends complete data
      const data = await fetchEnrichedBookingDetails(bookingId, accessToken);
      if (!data) throw new Error("Booking not found or access denied.");
      setBooking(data);
    } catch (err: any) {
      console.error(`Error fetching booking ${bookingId} details:`, err);
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  }, [bookingId, accessToken]);

  useEffect(() => {
    fetchBooking();
  }, [fetchBooking]);

  const getStatusVariant = (status: string) => {
    switch (status.toUpperCase()) {
      case 'CONFIRMED': case 'UPCOMING': return "default";
      case 'COMPLETED': return "secondary";
      case 'CANCELLED': return "destructive";
      default: return "outline";
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[calc(100vh-200px)]">
        <Loader2 className="h-16 w-16 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] text-center px-4">
        <AlertTriangle className="h-12 w-12 text-destructive mb-3" />
        <h2 className="text-xl font-semibold text-destructive mb-2">Error loading booking details</h2>
        <p className="text-sm text-muted-foreground mb-4">{error}</p>
        <Button variant="outline" onClick={() => router.push('/bookings')}>Back to My Bookings</Button>
      </div>
    );
  }

  if (!booking) {
    return (
      <div className="text-center py-10">
        <p className="text-xl text-muted-foreground">Booking not found.</p>
        <Link href="/bookings">
          <Button variant="link" className="mt-2"><ArrowLeft className="mr-2 h-4 w-4" /> Back to My Bookings</Button>
        </Link>
      </div>
    );
  }
  
  // Attempt to display names; fall back to IDs if names aren't available in the fetched booking object
  const courtName = booking.court?.name || `Court ID: ${booking.court_id}`;
  const clubName = booking.court?.club?.name || (booking.court?.club_id ? `Club ID: ${booking.court.club_id}` : 'Club details unavailable');
  const clubAddress = booking.court?.club?.address || '';
  const clubCity = booking.court?.club?.city || '';

  return (
    <div className="max-w-2xl mx-auto py-8 px-4 space-y-6">
      <Button variant="outline" size="sm" onClick={() => router.push('/bookings')} className="mb-4">
        <ArrowLeft className="mr-2 h-4 w-4" /> Back to My Bookings
      </Button>

      <Card>
        <CardHeader>
          <CardTitle className="text-2xl md:text-3xl font-bold">Booking Details</CardTitle>
          <div className="flex justify-between items-center">
            <CardDescription>ID: {booking.id}</CardDescription>
            <Badge variant={getStatusVariant(booking.status)} className="text-sm">{booking.status}</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold mb-2">Court Information</h3>
            <div className="space-y-1 text-sm">
                <p className="flex items-center"><Hash className="mr-2 h-4 w-4 text-muted-foreground" /> Court: {courtName}</p>
                <p className="flex items-center"><MapPin className="mr-2 h-4 w-4 text-muted-foreground" /> Club: {clubName}</p>
                {(clubAddress || clubCity) && <p className="ml-6 text-xs text-muted-foreground">{clubAddress}{clubAddress && clubCity ? ', ' : ''}{clubCity}</p>}
            </div>
          </div>
          <Separator />
          <div>
            <h3 className="text-lg font-semibold mb-2">Date & Time</h3>
            <div className="space-y-1 text-sm">
                <p className="flex items-center"><CalendarIcon className="mr-2 h-4 w-4 text-muted-foreground" /> Date: {format(parseISO(booking.start_time), 'PPP (EEEE)')}</p>
                <p className="flex items-center"><Clock className="mr-2 h-4 w-4 text-muted-foreground" /> Time: {format(parseISO(booking.start_time), 'HH:mm')} - {format(parseISO(booking.end_time), 'HH:mm')}</p>
            </div>
          </div>
          
          {/* Placeholder for future actions like 'Cancel Booking' or 'Invite Players' */}
          {/* <Separator />
          <div className="mt-4">
            <h3 className="text-lg font-semibold mb-2">Actions</h3>
            {booking.status.toUpperCase() === "CONFIRMED" && (
                <Button variant="destructive" size="sm" disabled>Cancel Booking (Coming Soon)</Button>
            )}
          </div> */}
        </CardContent>
      </Card>
    </div>
  );
}

const BookingDetailPage = () => (
    <Suspense fallback={<div className="flex justify-center items-center min-h-screen"><Loader2 className="h-12 w-12 animate-spin" /></div>}>
        <BookingDetailPageInternal />
    </Suspense>
);

export default withAuth(BookingDetailPage); 