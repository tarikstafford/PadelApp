"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Switch } from '@workspace/ui/components/switch';
import { Label } from '@workspace/ui/components/label';
import { Button } from '@workspace/ui/components/button';
import { Input } from '@workspace/ui/components/input';
import { Separator } from '@workspace/ui/components/separator';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';

interface NotificationPreferences {
  id: number;
  user_id: number;
  game_starting_enabled: boolean;
  game_ended_enabled: boolean;
  score_notifications_enabled: boolean;
  team_invitations_enabled: boolean;
  game_invitations_enabled: boolean;
  tournament_reminders_enabled: boolean;
  elo_updates_enabled: boolean;
  general_notifications_enabled: boolean;
  game_reminder_minutes: number;
  email_notifications_enabled: boolean;
  push_notifications_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export function NotificationPreferences() {
  const { accessToken } = useAuth();
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const fetchPreferences = async () => {
    if (!accessToken) return;
    
    setIsLoading(true);
    try {
      const response = await apiClient.get<NotificationPreferences>('/notifications/preferences', undefined, accessToken);
      setPreferences(response);
    } catch (error) {
      console.error('Error fetching notification preferences:', error);
      toast.error('Failed to load notification preferences');
    } finally {
      setIsLoading(false);
    }
  };

  const updatePreferences = async (updates: Partial<NotificationPreferences>) => {
    if (!accessToken || !preferences) return;
    
    setIsSaving(true);
    try {
      const response = await apiClient.put<NotificationPreferences>(
        '/notifications/preferences', 
        updates, 
        accessToken
      );
      setPreferences(response);
      toast.success('Notification preferences updated');
    } catch (error) {
      console.error('Error updating notification preferences:', error);
      toast.error('Failed to update notification preferences');
    } finally {
      setIsSaving(false);
    }
  };

  const handleToggle = (key: keyof NotificationPreferences) => {
    if (!preferences) return;
    
    const newValue = !preferences[key] as boolean;
    setPreferences(prev => prev ? { ...prev, [key]: newValue } : null);
    updatePreferences({ [key]: newValue });
  };

  const handleReminderMinutesChange = (minutes: number) => {
    if (!preferences) return;
    
    setPreferences(prev => prev ? { ...prev, game_reminder_minutes: minutes } : null);
    updatePreferences({ game_reminder_minutes: minutes });
  };

  useEffect(() => {
    fetchPreferences();
  }, [accessToken]);

  if (isLoading || !preferences) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Notification Preferences</CardTitle>
          <CardDescription>Loading your notification settings...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="h-4 bg-muted rounded w-1/2" />
                <div className="h-6 bg-muted rounded w-12" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const PreferenceToggle = ({ 
    id, 
    label, 
    description, 
    checked, 
    disabled = false 
  }: { 
    id: keyof NotificationPreferences; 
    label: string; 
    description: string; 
    checked: boolean; 
    disabled?: boolean;
  }) => (
    <div className="flex items-center justify-between space-x-4">
      <div className="flex-1">
        <Label htmlFor={id as string} className="text-sm font-medium">
          {label}
        </Label>
        <p className="text-xs text-muted-foreground mt-1">{description}</p>
      </div>
      <Switch
        id={id as string}
        checked={checked}
        onCheckedChange={() => handleToggle(id)}
        disabled={disabled || isSaving}
      />
    </div>
  );

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle>Notification Preferences</CardTitle>
        <CardDescription>
          Customize when and how you receive notifications about your games and activities.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Game Notifications */}
        <div>
          <h3 className="font-semibold mb-4">Game Notifications</h3>
          <div className="space-y-4">
            <PreferenceToggle
              id="game_starting_enabled"
              label="Game Starting Soon"
              description="Get notified when your games are about to start"
              checked={preferences.game_starting_enabled}
            />
            
            <PreferenceToggle
              id="game_ended_enabled"
              label="Game Ended"
              description="Get notified when your game time has ended"
              checked={preferences.game_ended_enabled}
            />
            
            <PreferenceToggle
              id="game_invitations_enabled"
              label="Game Invitations"
              description="Get notified when you're invited to join a game"
              checked={preferences.game_invitations_enabled}
            />
            
            <div className="flex items-center justify-between space-x-4">
              <div className="flex-1">
                <Label htmlFor="reminder-minutes" className="text-sm font-medium">
                  Game Reminder Time
                </Label>
                <p className="text-xs text-muted-foreground mt-1">
                  How many minutes before the game should we remind you?
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <Input
                  id="reminder-minutes"
                  type="number"
                  min="5"
                  max="120"
                  step="5"
                  value={preferences.game_reminder_minutes}
                  onChange={(e) => handleReminderMinutesChange(parseInt(e.target.value) || 30)}
                  className="w-20"
                  disabled={isSaving}
                />
                <span className="text-sm text-muted-foreground">min</span>
              </div>
            </div>
          </div>
        </div>

        <Separator />

        {/* Score Notifications */}
        <div>
          <h3 className="font-semibold mb-4">Score Notifications</h3>
          <div className="space-y-4">
            <PreferenceToggle
              id="score_notifications_enabled"
              label="Score Updates"
              description="Get notified about score submissions, confirmations, and disputes"
              checked={preferences.score_notifications_enabled}
            />
          </div>
        </div>

        <Separator />

        {/* Team & Tournament Notifications */}
        <div>
          <h3 className="font-semibold mb-4">Team & Tournament</h3>
          <div className="space-y-4">
            <PreferenceToggle
              id="team_invitations_enabled"
              label="Team Invitations"
              description="Get notified when you're invited to join a team"
              checked={preferences.team_invitations_enabled}
            />
            
            <PreferenceToggle
              id="tournament_reminders_enabled"
              label="Tournament Reminders"
              description="Get notified about upcoming tournament matches"
              checked={preferences.tournament_reminders_enabled}
            />
          </div>
        </div>

        <Separator />

        {/* Performance Notifications */}
        <div>
          <h3 className="font-semibold mb-4">Performance</h3>
          <div className="space-y-4">
            <PreferenceToggle
              id="elo_updates_enabled"
              label="ELO Rating Updates"
              description="Get notified when your ELO rating changes"
              checked={preferences.elo_updates_enabled}
            />
          </div>
        </div>

        <Separator />

        {/* General Notifications */}
        <div>
          <h3 className="font-semibold mb-4">General</h3>
          <div className="space-y-4">
            <PreferenceToggle
              id="general_notifications_enabled"
              label="General Notifications"
              description="Get notified about platform updates and announcements"
              checked={preferences.general_notifications_enabled}
            />
          </div>
        </div>

        <Separator />

        {/* Delivery Method (Future) */}
        <div>
          <h3 className="font-semibold mb-4">Delivery Method</h3>
          <div className="space-y-4">
            <PreferenceToggle
              id="push_notifications_enabled"
              label="In-App Notifications"
              description="Show notifications in the notification center"
              checked={preferences.push_notifications_enabled}
            />
            
            <PreferenceToggle
              id="email_notifications_enabled"
              label="Email Notifications"
              description="Send notifications to your email (coming soon)"
              checked={preferences.email_notifications_enabled}
              disabled={true}
            />
          </div>
        </div>

        {isSaving && (
          <div className="flex items-center justify-center py-4">
            <div className="text-sm text-muted-foreground">Saving preferences...</div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}