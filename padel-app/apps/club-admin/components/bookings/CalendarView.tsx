"use client";

import React,  { useState, useEffect, useCallback } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { DateSelectArg, EventClickArg, DatesSetArg } from '@fullcalendar/core';
import { transformBookingsToEvents, CalendarEvent } from '@/lib/calendarTransformers';
import { fetchBookings } from '@/lib/api';
import { Booking } from '@/lib/types';
import { useAuth } from '@/contexts/AuthContext';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import './CalendarView.css';
import BookingDetailsDialog from './BookingDetailsDialog';

interface CalendarViewProps {
  onEventClick?: (eventInfo: EventClickArg) => void;
  onDateSelect?: (selectionInfo: DateSelectArg) => void;
}

export default function CalendarView({ onDateSelect }: CalendarViewProps) {
  const { isAuthenticated } = useAuth();
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  
  const fetchAndSetBookings = useCallback(async (start: Date, end: Date) => {
    if (!isAuthenticated) return;
    setLoading(true);
    try {
      const bookings = await fetchBookings(start, end);
      const calendarEvents = transformBookingsToEvents(bookings);
      setEvents(calendarEvents);
    } catch (error: any) {
      console.error("Failed to fetch schedule", error);
      toast.error(error.message || "Could not load the schedule. Please try again later.");
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const handleDatesSet = useCallback((arg: DatesSetArg) => {
    fetchAndSetBookings(arg.start, arg.end);
  }, [fetchAndSetBookings]);

  const handleEventClick = (clickInfo: EventClickArg) => {
    const booking = clickInfo.event.extendedProps.booking as Booking;
    setSelectedBooking(booking);
    setIsDialogOpen(true);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setSelectedBooking(null);
  };
  
  return (
    <div className="calendar-container relative">
      {loading && (
        <div className="absolute inset-0 bg-white/50 flex items-center justify-center z-10">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      )}
      <FullCalendar
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,timeGridWeek,timeGridDay'
        }}
        initialView="dayGridMonth"
        weekends={true}
        events={events}
        selectable={true}
        editable={true}
        droppable={true}
        datesSet={handleDatesSet}
        eventClick={handleEventClick}
        select={onDateSelect}
        height="auto"
        dayMaxEvents={true}
        navLinks={true}
      />
      <BookingDetailsDialog
        booking={selectedBooking}
        isOpen={isDialogOpen}
        onClose={handleDialogClose}
      />
    </div>
  );
} 