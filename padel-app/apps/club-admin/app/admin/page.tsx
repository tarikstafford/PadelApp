"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card";
import { Skeleton } from "@workspace/ui/components/skeleton";
import { useDashboardData } from "@/hooks/useDashboardData";
import { BarChart, Calendar, Users, RefreshCw } from "lucide-react";
import Link from "next/link";
import { Button } from "@workspace/ui/components/button";
import { cn } from "@workspace/ui/lib/utils";
import { ClubProfileWidget } from "@/components/admin/club/club-profile-widget";

export default function AdminDashboardPage() {
  const clubId = 1;
  const { data, isLoading, error, isFetching, refetch } = useDashboardData(clubId);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Button onClick={() => refetch()} disabled={isFetching}>
          <RefreshCw
            className={cn("mr-2 h-4 w-4", isFetching && "animate-spin")}
          />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Today's Bookings</CardTitle>
              <CardDescription>Total bookings for today</CardDescription>
            </div>
            <Calendar className="h-5 w-5 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-12 w-24" />
            ) : error ? (
              <p className="text-destructive">Failed to load data</p>
            ) : (
              <div className="text-3xl font-bold">{data?.total_bookings_today || 0}</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Court Occupancy</CardTitle>
              <CardDescription>Percentage of courts booked</CardDescription>
            </div>
            <BarChart className="h-5 w-5 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-12 w-24" />
            ) : error ? (
              <p className="text-destructive">Failed to load data</p>
            ) : (
              <div className="text-3xl font-bold">
                {Math.round(data?.occupancy_rate_percent || 0)}%
              </div>
            )}
          </CardContent>
        </Card>

        {/* Club Profile Widget */}
        <ClubProfileWidget />
      </div>

      {/* Recent Activity Section */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest games and bookings</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array(3)
                .fill(0)
                .map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
            </div>
          ) : error ? (
            <p className="text-destructive">Failed to load data</p>
          ) : data?.recent_activity?.length ? (
            <ul className="space-y-2">
              {data.recent_activity.map((activity) => (
                <li
                  key={activity.game_id}
                  className="flex items-center justify-between border-b pb-2"
                >
                  <div>
                    <p className="font-medium">Game #{activity.game_id}</p>
                    <p className="text-sm text-muted-foreground">
                      {activity.player_count} players
                    </p>
                  </div>
                  <time className="text-sm text-muted-foreground">
                    {new Date(activity.created_at).toLocaleString()}
                  </time>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted-foreground">No recent activity</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 