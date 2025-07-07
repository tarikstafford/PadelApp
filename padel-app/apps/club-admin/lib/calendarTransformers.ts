/**
 * @module calendarTransformers
 * This module provides utility functions to transform booking data from the API
 * into a format compatible with the FullCalendar library.
 */

import { Booking, Tournament, TournamentMatch } from '@/lib/types';
import { EventInput } from '@fullcalendar/core';

export interface CalendarEvent extends EventInput {
  extendedProps: {
    booking?: Booking;
    tournament?: Tournament;
    tournamentMatch?: TournamentMatch;
    type: 'booking' | 'tournament' | 'tournament-match';
  };
}

/**
 * Determines the display colors for a calendar event based on the booking status.
 * @param {string} status - The status of the booking (e.g., 'CONFIRMED', 'PENDING', 'CANCELLED').
 * @returns {{ background: string, border: string, text: string }} - An object with color values.
 */
function getBookingStatusColors(status: string): { background: string; border: string; text: string } {
  switch (status.toUpperCase()) {
    case 'CONFIRMED':
      return { background: '#22c55e', border: '#16a34a', text: '#ffffff' }; // green-500, green-600
    case 'PENDING':
      return { background: '#f59e0b', border: '#d97706', text: '#ffffff' }; // amber-500, amber-600
    case 'CANCELLED':
      return { background: '#ef4444', border: '#dc2626', text: '#ffffff' }; // red-500, red-600
    default:
      return { background: '#a1a1aa', border: '#71717a', text: '#ffffff' }; // zinc-400, zinc-500
  }
}

/**
 * Transforms an array of booking objects from the API into an array of FullCalendar event objects.
 * @param {Booking[]} bookings - An array of booking objects.
 * @returns {CalendarEvent[]} - An array of objects formatted for FullCalendar.
 */
export function transformBookingsToEvents(bookings: Booking[]): CalendarEvent[] {
  if (!Array.isArray(bookings)) {
    console.error("transformBookingsToEvents: expected an array but received", bookings);
    return [];
  }

  return bookings.map(booking => {
    if (!booking || typeof booking !== 'object') {
      console.warn("transformBookingsToEvents: skipping invalid item in bookings array", booking);
      return null;
    }

    const {
      id,
      start_time,
      end_time,
      status,
      court,
      user,
    } = booking;

    if (!id || !start_time || !end_time || !status || !court || !user) {
      console.warn("transformBookingsToEvents: skipping booking with missing essential properties", booking);
      return null;
    }

    // Validate that start_time and end_time are valid dates
    const startTime = new Date(start_time);
    const endTime = new Date(end_time);

    if (isNaN(startTime.getTime()) || isNaN(endTime.getTime())) {
      console.warn("transformBookingsToEvents: skipping booking with invalid start_time or end_time", booking);
      return null;
    }

    const colors = getBookingStatusColors(status);
    
    const event: CalendarEvent = {
      id: `booking-${id}`,
      title: `${court.name}: ${user.name || user.email}`,
      start: startTime,
      end: endTime,
      backgroundColor: colors.background,
      borderColor: colors.border,
      textColor: colors.text,
      extendedProps: {
        booking,
        type: 'booking',
      },
    };
    return event;
  }).filter((event): event is CalendarEvent => event !== null);
}

/**
 * Determines the display colors for a tournament event based on the tournament status.
 */
function getTournamentStatusColors(status: string): { background: string; border: string; text: string } {
  switch (status.toUpperCase()) {
    case 'REGISTRATION_OPEN':
      return { background: '#10b981', border: '#047857', text: '#ffffff' }; // emerald-500, emerald-700
    case 'REGISTRATION_CLOSED':
      return { background: '#f59e0b', border: '#d97706', text: '#ffffff' }; // amber-500, amber-600
    case 'IN_PROGRESS':
      return { background: '#3b82f6', border: '#1d4ed8', text: '#ffffff' }; // blue-500, blue-700
    case 'COMPLETED':
      return { background: '#8b5cf6', border: '#7c3aed', text: '#ffffff' }; // violet-500, violet-600
    case 'CANCELLED':
      return { background: '#ef4444', border: '#dc2626', text: '#ffffff' }; // red-500, red-600
    case 'DRAFT':
    default:
      return { background: '#6b7280', border: '#4b5563', text: '#ffffff' }; // gray-500, gray-600
  }
}

/**
 * Determines the display colors for a tournament match based on the match status.
 */
function getTournamentMatchColors(status: string): { background: string; border: string; text: string } {
  switch (status.toUpperCase()) {
    case 'PENDING':
      return { background: '#f59e0b', border: '#d97706', text: '#ffffff' }; // amber-500, amber-600
    case 'IN_PROGRESS':
      return { background: '#3b82f6', border: '#1d4ed8', text: '#ffffff' }; // blue-500, blue-700
    case 'COMPLETED':
      return { background: '#10b981', border: '#047857', text: '#ffffff' }; // emerald-500, emerald-700
    case 'CANCELLED':
      return { background: '#ef4444', border: '#dc2626', text: '#ffffff' }; // red-500, red-600
    case 'POSTPONED':
    default:
      return { background: '#6b7280', border: '#4b5563', text: '#ffffff' }; // gray-500, gray-600
  }
}

/**
 * Transforms an array of tournament objects into FullCalendar events.
 */
export function transformTournamentsToEvents(tournaments: Tournament[]): CalendarEvent[] {
  if (!Array.isArray(tournaments)) {
    console.error("transformTournamentsToEvents: expected an array but received", tournaments);
    return [];
  }

  return tournaments.map(tournament => {
    if (!tournament || typeof tournament !== 'object') {
      console.warn("transformTournamentsToEvents: skipping invalid tournament", tournament);
      return null;
    }

    const {
      id,
      name,
      start_date,
      end_date,
      status,
      tournament_type,
    } = tournament;

    if (!id || !name || !start_date || !end_date || !status) {
      console.warn("transformTournamentsToEvents: skipping tournament with missing properties", tournament);
      return null;
    }

    const startTime = new Date(start_date);
    const endTime = new Date(end_date);

    if (isNaN(startTime.getTime()) || isNaN(endTime.getTime())) {
      console.warn("transformTournamentsToEvents: skipping tournament with invalid dates", tournament);
      return null;
    }

    const colors = getTournamentStatusColors(status);
    
    const event: CalendarEvent = {
      id: `tournament-${id}`,
      title: `🏆 ${name}`,
      start: startTime,
      end: endTime,
      backgroundColor: colors.background,
      borderColor: colors.border,
      textColor: colors.text,
      allDay: false,
      extendedProps: {
        tournament,
        type: 'tournament',
      },
    };
    return event;
  }).filter((event): event is CalendarEvent => event !== null);
}

/**
 * Transforms an array of tournament match objects into FullCalendar events.
 */
export function transformTournamentMatchesToEvents(matches: TournamentMatch[]): CalendarEvent[] {
  if (!Array.isArray(matches)) {
    console.error("transformTournamentMatchesToEvents: expected an array but received", matches);
    return [];
  }

  return matches.map(match => {
    if (!match || typeof match !== 'object') {
      console.warn("transformTournamentMatchesToEvents: skipping invalid match", match);
      return null;
    }

    const {
      id,
      tournament_id,
      team1_name,
      team2_name,
      scheduled_time,
      court_name,
      status,
      round_number,
      match_number,
    } = match;

    if (!id || !scheduled_time) {
      console.warn("transformTournamentMatchesToEvents: skipping match with missing essential properties", match);
      return null;
    }

    const startTime = new Date(scheduled_time);
    if (isNaN(startTime.getTime())) {
      console.warn("transformTournamentMatchesToEvents: skipping match with invalid scheduled_time", match);
      return null;
    }

    // Assume 1.5 hour duration for matches if no end time provided
    const endTime = new Date(startTime.getTime() + 90 * 60 * 1000);

    const colors = getTournamentMatchColors(status);
    
    const team1 = team1_name || 'TBD';
    const team2 = team2_name || 'TBD';
    const court = court_name ? ` (${court_name})` : '';
    
    const event: CalendarEvent = {
      id: `tournament-match-${id}`,
      title: `🎾 ${team1} vs ${team2}${court}`,
      start: startTime,
      end: endTime,
      backgroundColor: colors.background,
      borderColor: colors.border,
      textColor: colors.text,
      extendedProps: {
        tournamentMatch: match,
        type: 'tournament-match',
      },
    };
    return event;
  }).filter((event): event is CalendarEvent => event !== null);
}

/**
 * Combines bookings, tournaments, and tournament matches into a single array of calendar events.
 */
export function transformAllEventsToCalendar(data: {
  bookings?: Booking[];
  tournaments?: Tournament[];
  tournamentMatches?: TournamentMatch[];
}): CalendarEvent[] {
  const { bookings = [], tournaments = [], tournamentMatches = [] } = data;
  
  const bookingEvents = transformBookingsToEvents(bookings);
  const tournamentEvents = transformTournamentsToEvents(tournaments);
  const matchEvents = transformTournamentMatchesToEvents(tournamentMatches);
  
  return [...bookingEvents, ...tournamentEvents, ...matchEvents];
} 