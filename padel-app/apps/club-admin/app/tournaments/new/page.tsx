'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import { TournamentType, TournamentCategory, RecurrencePattern, TournamentCreateData, RecurringTournamentCreateData, HourlyTimeSlot } from '@/lib/types';
import CategorySelector, { CategoryConfig } from '@/components/tournaments/CategorySelector';
import TournamentTypeSelector from '@/components/tournaments/TournamentTypeSelector';
import TimeSlotPicker from '@/components/tournaments/TimeSlotPicker';
import RecurringConfig from '@/components/tournaments/RecurringConfig';
import { format, addDays } from 'date-fns';

interface Court {
  id: number;
  name: string;
}

export default function NewTournamentPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [courts, setCourts] = useState<Court[]>([]);
  const [isRecurring, setIsRecurring] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    tournament_type: '' as TournamentType | '',
    start_date: '',
    end_date: '',
    registration_deadline: '',
    max_participants: 32,
    entry_fee: 0,
    categories: [] as CategoryConfig[],
    court_ids: [] as number[],
  });
  
  const [recurringConfig, setRecurringConfig] = useState({
    series_name: '',
    recurrence_pattern: RecurrencePattern.WEEKLY,
    interval_value: 1,
    days_of_week: [] as number[],
    day_of_month: undefined as number | undefined,
    series_start_date: format(new Date(), 'yyyy-MM-dd'),
    series_end_date: undefined as string | undefined,
    duration_hours: 3,
    registration_deadline_hours: 24,
    advance_generation_days: 30,
    auto_generation_enabled: true,
  });
  
  const [selectedTimeSlots, setSelectedTimeSlots] = useState<HourlyTimeSlot[]>([]);

  useEffect(() => {
    fetchCourts();
  }, []);

  const fetchCourts = async () => {
    try {
      const data = await apiClient.get<Court[]>('/admin/my-club/courts');
      setCourts(data);
    } catch (error) {
      console.error('Failed to fetch courts:', error);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const updateCategories = (categories: CategoryConfig[]) => {
    setFormData(prev => ({ ...prev, categories }));
  };

  const toggleCourt = (courtId: number) => {
    setFormData(prev => ({
      ...prev,
      court_ids: prev.court_ids.includes(courtId)
        ? prev.court_ids.filter(id => id !== courtId)
        : [...prev.court_ids, courtId]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isRecurring) {
        const recurringData: RecurringTournamentCreateData = {
          series_name: recurringConfig.series_name || formData.name,
          description: formData.description,
          recurrence_pattern: recurringConfig.recurrence_pattern,
          interval_value: recurringConfig.interval_value,
          days_of_week: recurringConfig.days_of_week,
          day_of_month: recurringConfig.day_of_month,
          series_start_date: recurringConfig.series_start_date,
          series_end_date: recurringConfig.series_end_date,
          tournament_type: formData.tournament_type as TournamentType,
          duration_hours: recurringConfig.duration_hours,
          registration_deadline_hours: recurringConfig.registration_deadline_hours,
          max_participants: formData.max_participants,
          entry_fee: formData.entry_fee,
          advance_generation_days: recurringConfig.advance_generation_days,
          auto_generation_enabled: recurringConfig.auto_generation_enabled,
          category_templates: formData.categories.map(cat => ({
            category: cat.category,
            max_participants: cat.max_participants,
            min_elo: cat.min_elo || 1.0,
            max_elo: cat.max_elo || 5.0,
          })),
        };
        await apiClient.post('/recurring-tournaments', recurringData);
      } else {
        const tournamentData: TournamentCreateData = {
          name: formData.name,
          description: formData.description,
          tournament_type: formData.tournament_type as TournamentType,
          start_date: formData.start_date,
          end_date: formData.end_date,
          registration_deadline: formData.registration_deadline,
          entry_fee: formData.entry_fee,
          categories: formData.categories.map(cat => ({
            category: cat.category,
            max_participants: cat.max_participants,
          })),
          court_ids: formData.court_ids,
        };
        await apiClient.post('/tournaments', tournamentData);
      }
      router.push('/tournaments');
    } catch (error) {
      console.error('Error creating tournament:', error);
      alert(error instanceof Error ? error.message : 'Failed to create tournament');
    } finally {
      setLoading(false);
    }
  };

  const isFormValid = () => {
    const baseValid = formData.name && 
                     formData.tournament_type && 
                     formData.categories.length > 0 &&
                     formData.categories.every(cat => cat.category && cat.max_participants > 0);
    
    if (isRecurring) {
      return baseValid && 
             (recurringConfig.series_name || formData.name) &&
             recurringConfig.recurrence_pattern &&
             recurringConfig.series_start_date;
    }
    
    return baseValid &&
           formData.start_date && 
           formData.end_date && 
           formData.registration_deadline &&
           formData.court_ids.length > 0;
  };
  
  // Calculate default dates
  const defaultStartDate = format(addDays(new Date(), 7), "yyyy-MM-dd'T'HH:mm");
  const defaultEndDate = format(addDays(new Date(), 8), "yyyy-MM-dd'T'HH:mm");
  const defaultRegistrationDeadline = format(addDays(new Date(), 6), "yyyy-MM-dd'T'HH:mm");

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/tournaments">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Tournaments
          </Button>
        </Link>
        <h1 className="text-3xl font-bold">Create New Tournament</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Recurring Tournament Toggle */}
        <RecurringConfig
          enabled={isRecurring}
          onEnabledChange={setIsRecurring}
          config={recurringConfig}
          onConfigChange={setRecurringConfig}
        />
        
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
            <CardDescription>
              {isRecurring ? 'Set up the basic details for your tournament series' : 'Set up the basic details for your tournament'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">{isRecurring ? 'Series Name' : 'Tournament Name'} *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder={isRecurring ? "e.g., Weekly Americano Series" : "e.g., Spring Championship 2024"}
                  required
                />
              </div>
              <div>
                <Label htmlFor="entry_fee">Entry Fee ($)</Label>
                <Input
                  id="entry_fee"
                  type="number"
                  step="0.01"
                  value={formData.entry_fee}
                  onChange={(e) => handleInputChange('entry_fee', parseFloat(e.target.value))}
                  min="0"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder={isRecurring ? "Describe your tournament series..." : "Describe your tournament..."}
                rows={3}
              />
            </div>

            {!isRecurring && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="start_date">Start Date *</Label>
                    <Input
                      id="start_date"
                      type="datetime-local"
                      value={formData.start_date || defaultStartDate}
                      onChange={(e) => handleInputChange('start_date', e.target.value)}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="end_date">End Date *</Label>
                    <Input
                      id="end_date"
                      type="datetime-local"
                      value={formData.end_date || defaultEndDate}
                      onChange={(e) => handleInputChange('end_date', e.target.value)}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="registration_deadline">Registration Deadline *</Label>
                    <Input
                      id="registration_deadline"
                      type="datetime-local"
                      value={formData.registration_deadline || defaultRegistrationDeadline}
                      onChange={(e) => handleInputChange('registration_deadline', e.target.value)}
                      required
                    />
                  </div>
                </div>
              </>
            )}

            <div>
              <Label htmlFor="max_participants">Max Participants</Label>
              <Input
                id="max_participants"
                type="number"
                value={formData.max_participants}
                onChange={(e) => handleInputChange('max_participants', parseInt(e.target.value))}
                min="4"
                max="128"
              />
            </div>
          </CardContent>
        </Card>

        {/* Tournament Type Selection */}
        <TournamentTypeSelector
          value={formData.tournament_type}
          onChange={(type) => handleInputChange('tournament_type', type)}
        />

        {/* Category Configuration */}
        <CategorySelector
          categories={formData.categories}
          onChange={updateCategories}
          showEloRanges={isRecurring}
          requireEloRanges={isRecurring}
        />

        {/* Court Selection - Only for single tournaments */}
        {!isRecurring && (
          <>
            {/* Time Slot Selection */}
            {formData.start_date && formData.end_date && (
              <TimeSlotPicker
                selectedSlots={selectedTimeSlots}
                onChange={setSelectedTimeSlots}
                startDate={new Date(formData.start_date)}
                endDate={new Date(formData.end_date)}
              />
            )}
            
            <Card>
              <CardHeader>
                <CardTitle>Court Selection</CardTitle>
                <CardDescription>Select which courts will be used for this tournament</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {courts.map((court) => (
                    <div key={court.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={`court-${court.id}`}
                        checked={formData.court_ids.includes(court.id)}
                        onCheckedChange={() => toggleCourt(court.id)}
                      />
                      <Label htmlFor={`court-${court.id}`} className="text-sm">
                        {court.name}
                      </Label>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </>
        )}

        <div className="flex justify-end gap-4">
          <Link href="/tournaments">
            <Button type="button" variant="outline">Cancel</Button>
          </Link>
          <Button 
            type="submit" 
            disabled={!isFormValid() || loading}
          >
            {loading ? 'Creating...' : 'Create Tournament'}
          </Button>
        </div>
      </form>
    </div>
  );
}