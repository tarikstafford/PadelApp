"use client";

import React from 'react';
import { NotificationPreferences } from '@/components/notifications/notification-preferences';
import withAuth from '@/components/auth/withAuth';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@workspace/ui/components/button';

function NotificationSettingsPage() {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-6">
      <div className="flex items-center space-x-4 mb-6">
        <Link href="/profile">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Profile
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Notification Settings</h1>
          <p className="text-muted-foreground">
            Customize how and when you receive notifications about your games and activities.
          </p>
        </div>
      </div>

      <NotificationPreferences />
    </div>
  );
}

export default withAuth(NotificationSettingsPage);