"use client";

import { useEffect, useState } from 'react';
import { Calendar, TrendingUp, TrendingDown, DollarSign, Users, Trophy, Clock } from 'lucide-react';
import { useClub } from '@/contexts/ClubContext';
import { apiClient } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface BusinessMetrics {
  revenue: {
    total_revenue: number;
    booking_revenue: number;
    tournament_revenue: number;
    membership_revenue: number;
    growth_rate?: number;
    previous_period_revenue?: number;
  };
  bookings: {
    total_bookings: number;
    confirmed_bookings: number;
    cancelled_bookings: number;
    utilization_rate: number;
    average_duration: number;
    peak_hour?: number;
    unique_players: number;
  };
  tournaments: {
    active_tournaments: number;
    completed_tournaments: number;
    total_participants: number;
    tournament_revenue: number;
  };
}

export function BusinessMetricsOverview() {
  const { selectedClub } = useClub();
  const [metrics, setMetrics] = useState<BusinessMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    if (!selectedClub) return;

    setIsLoading(true);
    setError(null);

    try {
      // Get metrics for the current month
      const today = new Date();
      const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
      const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);

      const response = await apiClient.get<BusinessMetrics>(`/business/club/${selectedClub.id}/metrics`, {
        params: {
          start_date: firstDayOfMonth.toISOString().split('T')[0],
          end_date: lastDayOfMonth.toISOString().split('T')[0],
        },
      });

      setMetrics(response);
    } catch (err) {
      console.error('Failed to fetch business metrics:', err);
      setError('Failed to load business metrics');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, [selectedClub]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(8)].map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="h-4 w-24 bg-gray-200 animate-pulse rounded" />
              <div className="h-4 w-4 bg-gray-200 animate-pulse rounded" />
            </CardHeader>
            <CardContent>
              <div className="h-8 w-20 bg-gray-200 animate-pulse rounded mb-2" />
              <div className="h-3 w-32 bg-gray-200 animate-pulse rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-32">
          <p className="text-gray-500">{error || 'No metrics available'}</p>
        </CardContent>
      </Card>
    );
  }

  const growthIcon = metrics.revenue.growth_rate !== undefined 
    ? metrics.revenue.growth_rate >= 0 
      ? <TrendingUp className="h-4 w-4 text-green-600" />
      : <TrendingDown className="h-4 w-4 text-red-600" />
    : null;

  const growthColor = metrics.revenue.growth_rate !== undefined
    ? metrics.revenue.growth_rate >= 0 ? 'text-green-600' : 'text-red-600'
    : 'text-gray-500';

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {/* Total Revenue */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatCurrency(metrics.revenue.total_revenue)}
          </div>
          {metrics.revenue.growth_rate !== undefined && (
            <p className={`text-xs ${growthColor} flex items-center gap-1`}>
              {growthIcon}
              {Math.abs(metrics.revenue.growth_rate).toFixed(1)}% from last period
            </p>
          )}
        </CardContent>
      </Card>

      {/* Total Bookings */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Bookings</CardTitle>
          <Calendar className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.bookings.total_bookings}</div>
          <p className="text-xs text-muted-foreground">
            {metrics.bookings.confirmed_bookings} confirmed, {metrics.bookings.cancelled_bookings} cancelled
          </p>
        </CardContent>
      </Card>

      {/* Court Utilization */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Court Utilization</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatPercentage(metrics.bookings.utilization_rate)}
          </div>
          <p className="text-xs text-muted-foreground">
            Avg. {metrics.bookings.average_duration.toFixed(1)}h per booking
          </p>
        </CardContent>
      </Card>

      {/* Unique Players */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Unique Players</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.bookings.unique_players}</div>
          <p className="text-xs text-muted-foreground">
            Active this month
          </p>
        </CardContent>
      </Card>

      {/* Booking Revenue */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Booking Revenue</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatCurrency(metrics.revenue.booking_revenue)}
          </div>
          <p className="text-xs text-muted-foreground">
            {((metrics.revenue.booking_revenue / metrics.revenue.total_revenue) * 100).toFixed(0)}% of total
          </p>
        </CardContent>
      </Card>

      {/* Active Tournaments */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Active Tournaments</CardTitle>
          <Trophy className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.tournaments.active_tournaments}</div>
          <p className="text-xs text-muted-foreground">
            {metrics.tournaments.completed_tournaments} completed this month
          </p>
        </CardContent>
      </Card>

      {/* Tournament Revenue */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Tournament Revenue</CardTitle>
          <Trophy className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatCurrency(metrics.tournaments.tournament_revenue)}
          </div>
          <p className="text-xs text-muted-foreground">
            From {metrics.tournaments.total_participants} participants
          </p>
        </CardContent>
      </Card>

      {/* Peak Hour */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Peak Hour</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {metrics.bookings.peak_hour ? `${metrics.bookings.peak_hour}:00` : 'N/A'}
          </div>
          <p className="text-xs text-muted-foreground">
            Most popular booking time
          </p>
        </CardContent>
      </Card>
    </div>
  );
}