"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card";
import { Button } from "@workspace/ui/components/button";
import { useClubDetails } from "@/hooks/useClubDetails";
import { Skeleton } from "@workspace/ui/components/skeleton";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

export function ClubProfileWidget() {
  const { user } = useAuth();
  // For now, we'll assume the admin is associated with one club.
  // A club selection context would be needed for admins of multiple clubs.
  const clubId = user ? 1 : null; // Replace with actual club ID from user context
  const { data, isLoading, error } = useClubDetails(clubId);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Club Profile</CardTitle>
        <CardDescription>Manage your club details</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-4 w-2/3" />
          </div>
        ) : error ? (
          <p className="text-destructive">Failed to load club details</p>
        ) : data ? (
          <div className="space-y-4">
            <div>
              <h3 className="font-medium">{data.name}</h3>
              <p className="text-sm text-muted-foreground">{data.address}</p>
              <p className="text-sm text-muted-foreground">{data.email}</p>
            </div>
            
            <Link href="/admin/club">
              <Button>View & Edit Details</Button>
            </Link>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
} 