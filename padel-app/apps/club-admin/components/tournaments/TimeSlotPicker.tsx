'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Clock, Calendar } from 'lucide-react';
import { HourlyTimeSlot } from '@/lib/types';
import { format, parse, addHours, startOfDay, endOfDay, isAfter, isBefore, isSameDay } from 'date-fns';

interface TimeSlotPickerProps {
  selectedSlots: HourlyTimeSlot[];
  onChange: (slots: HourlyTimeSlot[]) => void;
  startDate: Date;
  endDate: Date;
  availableHoursStart?: number; // 0-23
  availableHoursEnd?: number; // 0-23
}

const DAYS_OF_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export default function TimeSlotPicker({
  selectedSlots,
  onChange,
  startDate,
  endDate,
  availableHoursStart = 8,
  availableHoursEnd = 22,
}: TimeSlotPickerProps) {
  const [selectedDay, setSelectedDay] = useState<Date>(startDate);
  
  // Generate all possible hourly slots for the selected day
  const generateDaySlots = (date: Date): HourlyTimeSlot[] => {
    const slots: HourlyTimeSlot[] = [];
    const dayStart = startOfDay(date);
    
    for (let hour = availableHoursStart; hour < availableHoursEnd; hour++) {
      const slotStart = addHours(dayStart, hour);
      const slotEnd = addHours(slotStart, 1);
      
      // Check if slot is within tournament dates
      if (isAfter(slotStart, startDate) || isSameDay(slotStart, startDate)) {
        if (isBefore(slotEnd, endDate) || isSameDay(slotEnd, endDate)) {
          slots.push({
            start_time: slotStart.toISOString(),
            end_time: slotEnd.toISOString(),
            day_of_week: slotStart.getDay() === 0 ? 6 : slotStart.getDay() - 1, // Convert to 0=Monday
            hour: hour,
          });
        }
      }
    }
    
    return slots;
  };

  const isSlotSelected = (slot: HourlyTimeSlot): boolean => {
    return selectedSlots.some(
      s => s.start_time === slot.start_time && s.end_time === slot.end_time
    );
  };

  const toggleSlot = (slot: HourlyTimeSlot) => {
    if (isSlotSelected(slot)) {
      onChange(selectedSlots.filter(
        s => !(s.start_time === slot.start_time && s.end_time === slot.end_time)
      ));
    } else {
      onChange([...selectedSlots, slot].sort(
        (a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
      ));
    }
  };

  const selectAllDay = (date: Date) => {
    const daySlots = generateDaySlots(date);
    const otherSlots = selectedSlots.filter(
      s => !isSameDay(new Date(s.start_time), date)
    );
    onChange([...otherSlots, ...daySlots].sort(
      (a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
    ));
  };

  const deselectAllDay = (date: Date) => {
    onChange(selectedSlots.filter(
      s => !isSameDay(new Date(s.start_time), date)
    ));
  };

  const formatHour = (hour: number): string => {
    return `${hour.toString().padStart(2, '0')}:00`;
  };

  // Generate date range for day selection
  const generateDateRange = (): Date[] => {
    const dates: Date[] = [];
    let current = new Date(startDate);
    
    while (isBefore(current, endDate) || isSameDay(current, endDate)) {
      dates.push(new Date(current));
      current = addHours(current, 24);
    }
    
    return dates;
  };

  const dateRange = generateDateRange();
  const currentDaySlots = generateDaySlots(selectedDay);
  const selectedDaySlotCount = currentDaySlots.filter(isSlotSelected).length;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Tournament Time Slots
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Day selector */}
        <div>
          <h4 className="text-sm font-medium mb-2">Select Day</h4>
          <div className="flex flex-wrap gap-2">
            {dateRange.map((date) => {
              const daySlotCount = selectedSlots.filter(
                s => isSameDay(new Date(s.start_time), date)
              ).length;
              return (
                <Button
                  key={date.toISOString()}
                  variant={isSameDay(selectedDay, date) ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedDay(date)}
                  className="relative"
                >
                  <Calendar className="h-4 w-4 mr-1" />
                  {format(date, 'MMM d')}
                  {daySlotCount > 0 && (
                    <Badge 
                      variant="secondary" 
                      className="ml-2 h-5 px-1 text-xs"
                    >
                      {daySlotCount}
                    </Badge>
                  )}
                </Button>
              );
            })}
          </div>
        </div>

        {/* Time slots for selected day */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <h4 className="text-sm font-medium">
              Time Slots for {format(selectedDay, 'EEEE, MMM d')}
            </h4>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => selectAllDay(selectedDay)}
                disabled={selectedDaySlotCount === currentDaySlots.length}
              >
                Select All
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => deselectAllDay(selectedDay)}
                disabled={selectedDaySlotCount === 0}
              >
                Clear Day
              </Button>
            </div>
          </div>
          
          <div className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2">
            {currentDaySlots.map((slot) => (
              <Button
                key={`${slot.start_time}-${slot.end_time}`}
                variant={isSlotSelected(slot) ? 'default' : 'outline'}
                size="sm"
                onClick={() => toggleSlot(slot)}
                className="text-xs"
              >
                {formatHour(slot.hour)}
              </Button>
            ))}
          </div>
        </div>

        {/* Summary */}
        <div className="pt-4 border-t">
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">
              Total selected time slots:
            </span>
            <Badge variant="secondary">
              {selectedSlots.length} hour{selectedSlots.length !== 1 ? 's' : ''}
            </Badge>
          </div>
          {selectedSlots.length > 0 && (
            <div className="mt-2 text-xs text-muted-foreground">
              Tournament will require approximately {selectedSlots.length} hours of court time
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}