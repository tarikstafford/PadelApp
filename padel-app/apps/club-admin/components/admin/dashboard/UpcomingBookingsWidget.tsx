"use client";

import { useEffect, useState } from 'react';
import { Calendar, Clock, MapPin, User, GamepadIcon } from 'lucide-react';
import { useClub } from '@/contexts/ClubContext';
import { apiClient } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface UpcomingBooking {
  id: number;
  court_name: string;
  court_id: number;
  user_name: string;
  user_id: number;
  start_time: string;
  end_time: string;
  status: string;
  has_game: boolean;
}

export function UpcomingBookingsWidget() {
  const { selectedClub } = useClub();
  const [bookings, setBookings] = useState<UpcomingBooking[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [daysAhead, setDaysAhead] = useState(7);

  const fetchUpcomingBookings = async () => {
    if (!selectedClub) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<UpcomingBooking[]>(`/business/club/${selectedClub.id}/upcoming-bookings`, {
        params: { days_ahead: daysAhead },
      });

      setBookings(response);
    } catch (err) {
      console.error('Failed to fetch upcoming bookings:', err);
      setError('Failed to load upcoming bookings');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUpcomingBookings();
  }, [selectedClub, daysAhead]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'confirmed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const isToday = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isTomorrow = (dateString: string) => {
    const date = new Date(dateString);
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return date.toDateString() === tomorrow.toDateString();
  };

  const getDateLabel = (dateString: string) => {
    if (isToday(dateString)) return 'Today';
    if (isTomorrow(dateString)) return 'Tomorrow';
    return formatDate(dateString);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Upcoming Bookings</CardTitle>
            <CardDescription>
              Next {daysAhead} days • {bookings.length} bookings
            </CardDescription>
          </div>
          <div className="flex space-x-2">
            <Button
              variant={daysAhead === 3 ? 'default' : 'outline'}
              size="sm"
              onClick={() => setDaysAhead(3)}
            >
              3 days
            </Button>
            <Button
              variant={daysAhead === 7 ? 'default' : 'outline'}
              size="sm"
              onClick={() => setDaysAhead(7)}
            >
              7 days
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex items-center space-x-3 p-3 border rounded-lg">
                <div className="h-4 w-16 bg-gray-200 animate-pulse rounded" />
                <div className="flex-1">
                  <div className="h-4 w-32 bg-gray-200 animate-pulse rounded mb-1" />
                  <div className="h-3 w-24 bg-gray-200 animate-pulse rounded" />
                </div>
                <div className="h-6 w-16 bg-gray-200 animate-pulse rounded" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-8 text-gray-500">
            <p>{error}</p>
            <Button variant="outline" onClick={fetchUpcomingBookings} className="mt-2">
              Try Again
            </Button>
          </div>
        ) : bookings.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Calendar className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No upcoming bookings</p>
            <p className="text-sm">Check back later or extend the date range</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {bookings.map((booking) => (
              <div
                key={booking.id}
                className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="text-sm text-gray-600 min-w-16">
                  <div className="font-medium">{getDateLabel(booking.start_time)}</div>
                  <div className="text-xs">
                    {formatTime(booking.start_time)} - {formatTime(booking.end_time)}
                  </div>
                </div>

                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <MapPin className="h-3 w-3 text-gray-400" />
                    <span className="text-sm font-medium">{booking.court_name}</span>
                    {booking.has_game && (
                      <GamepadIcon className="h-3 w-3 text-blue-500" />
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <User className="h-3 w-3 text-gray-400" />
                    <span className="text-sm text-gray-600">{booking.user_name}</span>
                  </div>
                </div>

                <Badge className={getStatusColor(booking.status)} variant="secondary">
                  {booking.status}
                </Badge>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}