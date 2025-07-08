"use client";

import React,  { useState, useCallback } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { DateSelectArg, EventClickArg, DatesSetArg } from '@fullcalendar/core';
import { transformAllEventsToCalendar, CalendarEvent } from '@/lib/calendarTransformers';
import { fetchBookings, apiClient } from '@/lib/api';
import { Booking, Tournament, TournamentMatch } from '@/lib/types';
import { useAuth } from '@/contexts/AuthContext';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import './CalendarView.css';
import BookingDetailsDialog from './BookingDetailsDialog';
import TournamentDetailsDialog from '@/components/tournaments/TournamentDetailsDialog';
import TournamentMatchDialog from '@/components/tournaments/TournamentMatchDialog';

interface CalendarViewProps {
  onEventClick?: (eventInfo: EventClickArg) => void;
  onDateSelect?: (selectionInfo: DateSelectArg) => void;
}

export default function CalendarView({ onDateSelect }: CalendarViewProps) {
  const { user, isAuthenticated } = useAuth();
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);
  const [selectedTournament, setSelectedTournament] = useState<Tournament | null>(null);
  const [selectedMatch, setSelectedMatch] = useState<TournamentMatch | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  
  const fetchAndSetEvents = useCallback(async (start: Date, end: Date) => {
    if (!isAuthenticated || !user?.club_id) return;
    setLoading(true);
    try {
      const startDate = start.toISOString().split("T")[0];
      const endDate = end.toISOString().split("T")[0];
      
      // Fetch bookings
      const bookingsData = await fetchBookings(user.club_id, {
        start_date: startDate,
        end_date: endDate,
      });
      
      // Fetch tournaments
      const tournamentsData = await apiClient.get<Tournament[]>('/tournaments/club', {
        start_date: startDate,
        end_date: endDate,
      });
      
      // Fetch tournament matches (if any tournaments exist)
      let matchesData: TournamentMatch[] = [];
      if (tournamentsData.length > 0) {
        try {
          matchesData = await apiClient.get<TournamentMatch[]>('/tournaments/matches', {
            start_date: startDate,
            end_date: endDate,
          });
        } catch (error) {
          // Matches endpoint might not exist yet, continue without matches
          console.warn("Could not fetch tournament matches:", error);
        }
      }
      
      // Transform all events and combine them
      const calendarEvents = transformAllEventsToCalendar({
        bookings: bookingsData.bookings,
        tournaments: tournamentsData,
        tournamentMatches: matchesData,
      });
      
      setEvents(calendarEvents);
    } catch (error: unknown) {
      console.error("Failed to fetch schedule", error);
      toast.error((error instanceof Error ? error.message : String(error)) || "Could not load the schedule. Please try again later.");
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, user?.club_id]);

  const handleDatesSet = useCallback((arg: DatesSetArg) => {
    fetchAndSetEvents(arg.start, arg.end);
  }, [fetchAndSetEvents]);

  const handleEventClick = (clickInfo: EventClickArg) => {
    const { extendedProps } = clickInfo.event;
    
    // Clear all selections first
    setSelectedBooking(null);
    setSelectedTournament(null);
    setSelectedMatch(null);
    
    // Set the appropriate selection based on event type
    switch (extendedProps.type) {
      case 'booking':
        setSelectedBooking(extendedProps.booking as Booking);
        break;
      case 'tournament':
        setSelectedTournament(extendedProps.tournament as Tournament);
        break;
      case 'tournament-match':
        setSelectedMatch(extendedProps.tournamentMatch as TournamentMatch);
        break;
    }
    
    setIsDialogOpen(true);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setSelectedBooking(null);
    setSelectedTournament(null);
    setSelectedMatch(null);
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
        isOpen={isDialogOpen && !!selectedBooking}
        onClose={handleDialogClose}
      />
      <TournamentDetailsDialog
        tournament={selectedTournament}
        isOpen={isDialogOpen && !!selectedTournament}
        onClose={handleDialogClose}
      />
      <TournamentMatchDialog
        match={selectedMatch}
        isOpen={isDialogOpen && !!selectedMatch}
        onClose={handleDialogClose}
      />
    </div>
  );
} 