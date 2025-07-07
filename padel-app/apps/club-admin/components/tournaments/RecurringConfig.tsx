'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Calendar, Clock, Info } from 'lucide-react';
import { RecurrencePattern } from '@/lib/types';
import { format } from 'date-fns';

interface RecurringConfigProps {
  enabled: boolean;
  onEnabledChange: (enabled: boolean) => void;
  config: {
    recurrence_pattern: RecurrencePattern;
    interval_value: number;
    days_of_week?: number[];
    day_of_month?: number;
    series_end_date?: string;
    duration_hours: number;
    registration_deadline_hours: number;
    advance_generation_days: number;
    auto_generation_enabled: boolean;
  };
  onConfigChange: (config: any) => void;
}

const DAYS_OF_WEEK = [
  { value: 0, label: 'Monday', short: 'Mon' },
  { value: 1, label: 'Tuesday', short: 'Tue' },
  { value: 2, label: 'Wednesday', short: 'Wed' },
  { value: 3, label: 'Thursday', short: 'Thu' },
  { value: 4, label: 'Friday', short: 'Fri' },
  { value: 5, label: 'Saturday', short: 'Sat' },
  { value: 6, label: 'Sunday', short: 'Sun' },
];

export default function RecurringConfig({ 
  enabled, 
  onEnabledChange, 
  config, 
  onConfigChange 
}: RecurringConfigProps) {
  const updateConfig = (field: string, value: any) => {
    onConfigChange({ ...config, [field]: value });
  };

  const toggleDayOfWeek = (day: number) => {
    const currentDays = config.days_of_week || [];
    const updated = currentDays.includes(day)
      ? currentDays.filter(d => d !== day)
      : [...currentDays, day].sort();
    updateConfig('days_of_week', updated);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Recurring Tournament Series</CardTitle>
            <CardDescription>
              Set up a repeating tournament schedule
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Switch
              id="recurring-enabled"
              checked={enabled}
              onCheckedChange={onEnabledChange}
            />
            <Label htmlFor="recurring-enabled">Enable</Label>
          </div>
        </div>
      </CardHeader>
      
      {enabled && (
        <CardContent className="space-y-6">
          {/* Recurrence Pattern */}
          <div className="space-y-4">
            <div>
              <Label htmlFor="recurrence-pattern">Recurrence Pattern</Label>
              <Select
                value={config.recurrence_pattern}
                onValueChange={(value) => updateConfig('recurrence_pattern', value as RecurrencePattern)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select pattern" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={RecurrencePattern.DAILY}>Daily</SelectItem>
                  <SelectItem value={RecurrencePattern.WEEKLY}>Weekly</SelectItem>
                  <SelectItem value={RecurrencePattern.MONTHLY}>Monthly</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Interval */}
            <div>
              <Label htmlFor="interval">
                Repeat every {config.recurrence_pattern === RecurrencePattern.DAILY ? 'day' : 
                              config.recurrence_pattern === RecurrencePattern.WEEKLY ? 'week' : 'month'}
              </Label>
              <Input
                id="interval"
                type="number"
                min="1"
                max="12"
                value={config.interval_value}
                onChange={(e) => updateConfig('interval_value', parseInt(e.target.value))}
              />
            </div>

            {/* Days of week for weekly recurrence */}
            {config.recurrence_pattern === RecurrencePattern.WEEKLY && (
              <div>
                <Label>Days of the Week</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {DAYS_OF_WEEK.map((day) => (
                    <Badge
                      key={day.value}
                      variant={(config.days_of_week || []).includes(day.value) ? 'default' : 'outline'}
                      className="cursor-pointer"
                      onClick={() => toggleDayOfWeek(day.value)}
                    >
                      {day.short}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Day of month for monthly recurrence */}
            {config.recurrence_pattern === RecurrencePattern.MONTHLY && (
              <div>
                <Label htmlFor="day-of-month">Day of Month</Label>
                <Input
                  id="day-of-month"
                  type="number"
                  min="1"
                  max="31"
                  value={config.day_of_month || ''}
                  onChange={(e) => updateConfig('day_of_month', parseInt(e.target.value))}
                  placeholder="1-31"
                />
              </div>
            )}
          </div>

          {/* Tournament Configuration */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Tournament Settings
            </h4>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="duration-hours">Duration (hours)</Label>
                <Input
                  id="duration-hours"
                  type="number"
                  min="1"
                  max="24"
                  value={config.duration_hours}
                  onChange={(e) => updateConfig('duration_hours', parseInt(e.target.value))}
                />
              </div>
              
              <div>
                <Label htmlFor="registration-deadline">
                  Registration Closes (hours before)
                </Label>
                <Input
                  id="registration-deadline"
                  type="number"
                  min="1"
                  max="168"
                  value={config.registration_deadline_hours}
                  onChange={(e) => updateConfig('registration_deadline_hours', parseInt(e.target.value))}
                />
              </div>
            </div>
          </div>

          {/* Series End Date */}
          <div>
            <Label htmlFor="series-end-date">Series End Date (Optional)</Label>
            <Input
              id="series-end-date"
              type="date"
              value={config.series_end_date ? format(new Date(config.series_end_date), 'yyyy-MM-dd') : ''}
              onChange={(e) => updateConfig('series_end_date', e.target.value || undefined)}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Leave empty for an ongoing series
            </p>
          </div>

          {/* Advanced Settings */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium">Advanced Settings</h4>
            
            <div>
              <Label htmlFor="advance-generation">
                Generate tournaments in advance (days)
              </Label>
              <Input
                id="advance-generation"
                type="number"
                min="7"
                max="365"
                value={config.advance_generation_days}
                onChange={(e) => updateConfig('advance_generation_days', parseInt(e.target.value))}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Tournaments will be created this many days before they start
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="auto-generation"
                checked={config.auto_generation_enabled}
                onCheckedChange={(checked) => updateConfig('auto_generation_enabled', checked)}
              />
              <Label htmlFor="auto-generation">
                Automatically generate future tournaments
              </Label>
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-muted p-4 rounded-lg">
            <div className="flex gap-2">
              <Info className="h-4 w-4 mt-0.5 text-muted-foreground" />
              <div className="text-sm text-muted-foreground">
                <p>This will create a series of tournaments that repeat according to your schedule.</p>
                <p className="mt-1">
                  Example: "Weekly Americano every Wednesday at 7pm"
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
}