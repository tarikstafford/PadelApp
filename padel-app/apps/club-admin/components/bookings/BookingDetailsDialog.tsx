"use client";

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@workspace/ui/components/dialog";
import { Badge } from "@workspace/ui/components/badge";
import { format } from "date-fns";
import { Booking } from "@/lib/types";
import { CalendarIcon, ClockIcon, UserIcon, TagIcon, HashIcon } from 'lucide-react';

interface BookingDetailsDialogProps {
  booking: Booking | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function BookingDetailsDialog({ booking, isOpen, onClose }: BookingDetailsDialogProps) {
  if (!booking) return null;
  
  const getStatusVariant = (status: string): "default" | "outline" | "destructive" | "secondary" => {
    switch (status.toUpperCase()) {
      case 'CONFIRMED': return "secondary";
      case 'PENDING': return "default";
      case 'CANCELLED': return "destructive";
      default: return "outline";
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[480px]">
        <DialogHeader>
          <DialogTitle>Booking Details</DialogTitle>
          <DialogDescription>
            Detailed information for booking #{booking.id}.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground flex items-center"><TagIcon className="mr-2 h-4 w-4" />Status</span>
            <Badge variant={getStatusVariant(booking.status)}>
              {booking.status}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground flex items-center"><UserIcon className="mr-2 h-4 w-4" />Player</span>
            <span>{booking.user.name} ({booking.user.email})</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground flex items-center"><HashIcon className="mr-2 h-4 w-4" />Court</span>
            <span>{booking.court.name}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground flex items-center"><CalendarIcon className="mr-2 h-4 w-4" />Date</span>
            <span>{format(new Date(booking.start_time), 'PPP')}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground flex items-center"><ClockIcon className="mr-2 h-4 w-4" />Time</span>
            <span>{format(new Date(booking.start_time), 'p')} - {format(new Date(booking.end_time), 'p')}</span>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
} 