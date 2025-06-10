"use client";

import { useState } from "react";
import { Calendar } from "@workspace/ui/components/calendar";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card";
import { useCourtSchedule } from "@/hooks/useCourtSchedule";
import { Skeleton } from "@workspace/ui/components/skeleton";
import { Booking } from "@/lib/types";
import { BookingDetailsDialog } from "@/components/admin/bookings/booking-details-dialog";

// Helper functions
function generateTimeSlots(start: string, end: string, intervalMinutes: number): string[] {
  const slots: string[] = [];
  const startTime = new Date(`2000-01-01T${start}:00`);
  const endTime = new Date(`2000-01-01T${end}:00`);

  let currentTime = startTime;
  while (currentTime < endTime) {
    slots.push(currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }));
    currentTime = new Date(currentTime.getTime() + intervalMinutes * 60000);
  }

  return slots;
}

function findBookingForTimeSlot(courtId: number, timeSlot: string, bookings: Booking[]): Booking | undefined {
  return bookings.find((booking) => {
    if (booking.court_id !== courtId) return false;
    
    const slotTime = parseTimeString(timeSlot);
    const bookingStartTime = new Date(booking.start_time);
    const startTime = parseTimeString(bookingStartTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }));
    
    return slotTime.getTime() === startTime.getTime();
  });
}

function parseTimeString(timeStr: string): Date {
  const [hours, minutes] = timeStr.split(':').map(Number);
  const date = new Date();
  date.setHours(hours, minutes, 0, 0);
  return date;
}

function getBookingTimeSpan(booking: Booking, intervalMinutes: number): number {
  const startTime = new Date(booking.start_time);
  const endTime = new Date(booking.end_time);
  const durationMinutes = (endTime.getTime() - startTime.getTime()) / 60000;
  return Math.round(durationMinutes / intervalMinutes);
}

function getBookingColorClass(status: string): string {
  switch (status) {
    case 'CONFIRMED': return 'bg-green-100 text-green-800';
    case 'PENDING': return 'bg-yellow-100 text-yellow-800';
    case 'CANCELLED': return 'bg-red-100 text-red-800';
    default: return 'bg-gray-100 text-gray-800';
  }
}

export default function SchedulePage() {
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date());
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const timeSlots = generateTimeSlots('08:00', '22:00', 30);
  const clubId = 1; // Hardcoded for now
  const { data, isLoading, error } = useCourtSchedule(clubId, selectedDate);

  const courts = data?.courts || [];
  const bookings = data?.bookings || [];

  const handleBookingClick = (booking: Booking) => {
    setSelectedBooking(booking);
    setIsDialogOpen(true);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Court Schedule</h1>

      <div className="flex flex-col md:flex-row gap-6">
        <Card className="md:w-80">
          <CardHeader>
            <CardTitle>Select Date</CardTitle>
          </CardHeader>
          <CardContent>
            <Calendar
              mode="single"
              selected={selectedDate}
              onSelect={setSelectedDate}
              className="rounded-md border"
            />
          </CardContent>
        </Card>

        <div className="flex-1">
          <Card>
            <CardHeader>
              <CardTitle>
                Schedule for {selectedDate?.toLocaleDateString()}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <div className="min-w-[800px]">
                  {/* Header row with time slots */}
                  <div
                    className="grid border-b"
                    style={{
                      gridTemplateColumns: `150px repeat(${timeSlots.length}, minmax(100px, 1fr))`,
                    }}
                  >
                    <div className="p-2 font-medium">Court</div>
                    {timeSlots.map((slot) => (
                      <div key={slot} className="p-2 text-center text-sm font-medium">
                        {slot}
                      </div>
                    ))}
                  </div>
                  {/* Court rows */}
                  {isLoading ? (
                    <div className="p-2">
                      <Skeleton className="h-12 w-full" />
                    </div>
                  ) : error ? (
                    <p className="p-2 text-destructive">Failed to load schedule</p>
                  ) : courts?.length ? (
                    courts.map((court) => {
                      if (!court) return null;
                      return (
                        <div
                          key={court.id}
                          className="grid border-b"
                          style={{
                            gridTemplateColumns: `150px repeat(${timeSlots.length}, minmax(100px, 1fr))`,
                          }}
                        >
                          <div className="p-2 font-medium">{court.name}</div>
                          {/* Time slot cells */}
                          {timeSlots.map((slot) => {
                            const booking = findBookingForTimeSlot(court.id as number, slot, bookings);
                            
                            if (booking) {
                              const timeSpan = getBookingTimeSpan(booking, 30);
                              return (
                                <div
                                  key={`${court.id}-${slot}`}
                                  className={`p-1 border-r min-h-[50px]`}
                                  style={{ gridColumn: `span ${timeSpan}` }}
                                >
                                  <div
                                    className={`h-full rounded p-1 text-xs cursor-pointer ${getBookingColorClass(booking.status)}`}
                                  >
                                    {booking.user?.name || 'Unnamed'}
                                  </div>
                                </div>
                              );
                            }
                            
                            return (
                              <div key={`${court.id}-${slot}`} className="p-1 border-r min-h-[50px]">
                                {/* Empty slot */}
                              </div>
                            );
                          })}
                        </div>
                      )
                    })
                  ) : (
                    <p className="p-2 text-muted-foreground">No courts available</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 