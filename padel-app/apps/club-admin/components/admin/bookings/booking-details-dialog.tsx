"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@workspace/ui/components/dialog";
import { Skeleton } from "@workspace/ui/components/skeleton";
import { Badge } from "@workspace/ui/components/badge";
import { useGameDetails } from "@/hooks/useGameDetails";
import { Booking } from "@/lib/types";
import { Avatar, AvatarFallback, AvatarImage } from "@workspace/ui/components/avatar";

interface BookingDetailsDialogProps {
  booking: Booking | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const getStatusVariant = (status: string) => {
  switch (status) {
    case "CONFIRMED":
      return "default";
    case "PENDING":
      return "secondary";
    case "CANCELLED":
      return "destructive";
    default:
      return "outline";
  }
};

export function BookingDetailsDialog({
  booking,
  open,
  onOpenChange,
}: BookingDetailsDialogProps) {
  const { data: game, isLoading, error } = useGameDetails(booking?.id || null);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Booking Details</DialogTitle>
        </DialogHeader>

        {booking ? (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Date</h3>
                <p>{new Date(booking.start_time).toLocaleDateString()}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Time</h3>
                <p>{`${new Date(booking.start_time).toLocaleTimeString()} - ${new Date(
                  booking.end_time
                ).toLocaleTimeString()}`}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Court</h3>
                <p>{booking.court.name}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Status</h3>
                <Badge variant={getStatusVariant(booking.status)}>
                  {booking.status}
                </Badge>
              </div>
            </div>
            {isLoading ? (
              <Skeleton className="h-24 w-full" />
            ) : error ? (
              <p className="text-destructive">Failed to load game details</p>
            ) : game ? (
              <div>
                <h3 className="text-lg font-medium">Game #{game.id}</h3>
                <p className="text-sm text-muted-foreground">
                  Created {new Date(game.created_at).toLocaleString()}
                </p>
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-muted-foreground mb-2">
                    Players
                  </h4>
                  <div className="space-y-2">
                    {game.players.map((player) => (
                      <div
                        key={player.id}
                        className="flex items-center justify-between border-b pb-2"
                      >
                        <div className="flex items-center gap-2">
                          <Avatar>
                            <AvatarImage src={player.user.profile_picture_url} />
                            <AvatarFallback>
                              {player.user.name?.charAt(0)}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium">{player.user.name}</p>
                            <p className="text-sm text-muted-foreground">
                              {player.user.email}
                            </p>
                          </div>
                        </div>
                        <Badge
                          variant={
                            player.status === "accepted" ? "default" : "secondary"
                          }
                        >
                          {player.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground">
                No game associated with this booking
              </p>
            )}
          </div>
        ) : (
          <p>No booking selected</p>
        )}
      </DialogContent>
    </Dialog>
  );
} 