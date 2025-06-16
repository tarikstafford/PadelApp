/**
 * @module calendarTransformers
 * This module provides utility functions to transform booking data from the API
 * into a format compatible with the FullCalendar library.
 */

import { Booking } from '@/lib/types';
import { EventInput } from '@fullcalendar/core';

export interface CalendarEvent extends EventInput {
  extendedProps: {
    booking: Booking;
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
      },
    };
    return event;
  }).filter((event): event is CalendarEvent => event !== null);
} 