"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { apiClient } from "@/lib/api";
import { Booking } from "@/lib/types";
import { Button } from "@workspace/ui/components/button";
import { Card, CardContent, CardHeader, CardTitle } from "@workspace/ui/components/card";
import { BookOpenCheck } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import { format } from "date-fns";

export default function BookingsPage() {
  const { user } = useAuth();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      setLoading(true);
      apiClient.get<Booking[]>("/admin/my-club/bookings")
        .then(data => {
          setBookings(data);
        })
        .catch(error => {
          console.error("Failed to fetch bookings", error);
          toast.error("Could not load your bookings. Please try again later.");
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [user]);

  if (loading) {
    return <div>Loading bookings...</div>;
  }

  if (bookings.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center p-8 border-2 border-dashed rounded-lg h-64">
        <BookOpenCheck className="w-16 h-16 mb-4 text-gray-400" />
        <h2 className="text-2xl font-bold mb-2">No Bookings Yet</h2>
        <p className="mb-4 text-gray-600">You do not have any bookings for your club at the moment.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Your Club's Bookings</h1>
      <div className="grid gap-4">
        {bookings.map(booking => (
          <Card key={booking.id}>
            <CardHeader>
              <CardTitle>Booking for {booking.court.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p><strong>User:</strong> {booking.user.full_name} ({booking.user.email})</p>
              <p><strong>Time:</strong> {format(new Date(booking.start_time), "PPP p")} - {format(new Date(booking.end_time), "p")}</p>
              <p><strong>Status:</strong> {booking.status}</p>
              <p><strong>Price:</strong> ${booking.total_price}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
} 