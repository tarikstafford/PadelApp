"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@workspace/ui/components/card";
import { useAuth } from '@/contexts/AuthContext';
import CalendarView from '@/components/bookings/CalendarView';
import { Skeleton } from '@workspace/ui/components/skeleton';

export default function BookingsPage() {
  const { user, isLoading: isAuthLoading } = useAuth();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthLoading) {
      setLoading(false);
    }
  }, [isAuthLoading]);

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <Card>
          <CardHeader>
            <Skeleton className="h-8 w-1/2" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-96 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!user) {
    return <div>Please log in to view bookings.</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Bookings Calendar</h1>
      <Card>
        <CardContent className="p-0">
          <CalendarView />
        </CardContent>
      </Card>
    </div>
  );
} 