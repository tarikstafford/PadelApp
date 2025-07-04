"use client";

import { RefreshCw } from "lucide-react";
import { Button } from "@workspace/ui/components/button";
import { cn } from "@workspace/ui/lib/utils";
import { useState } from "react";
import { useClub } from "@/contexts/ClubContext";
import { ClubSwitcher } from "@/components/admin/ClubSwitcher";
import { BusinessMetricsOverview } from "@/components/admin/dashboard/BusinessMetricsOverview";
import { UpcomingBookingsWidget } from "@/components/admin/dashboard/UpcomingBookingsWidget";
import { TournamentStatusWidget } from "@/components/admin/dashboard/TournamentStatusWidget";

export default function AdminDashboardPage() {
  const { selectedClub, isMultiClubMode } = useClub();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Add a small delay to show the refresh animation
    setTimeout(() => {
      window.location.reload();
    }, 500);
  };

  if (!selectedClub) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <ClubSwitcher />
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <h2 className="text-xl font-semibold mb-2">No Club Selected</h2>
            <p className="text-gray-500">Please select a club to view the dashboard</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Club Switcher */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          {isMultiClubMode && <ClubSwitcher />}
        </div>
        <Button onClick={handleRefresh} disabled={isRefreshing}>
          <RefreshCw
            className={cn("mr-2 h-4 w-4", isRefreshing && "animate-spin")}
          />
          Refresh
        </Button>
      </div>

      {/* Club Name Display for Single Club Mode */}
      {!isMultiClubMode && (
        <div className="flex items-center space-x-2">
          <ClubSwitcher />
        </div>
      )}

      {/* Business Metrics Overview */}
      <BusinessMetricsOverview key={`metrics-${selectedClub.id}`} />

      {/* Widgets Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <UpcomingBookingsWidget key={`bookings-${selectedClub.id}`} />
        <TournamentStatusWidget key={`tournaments-${selectedClub.id}`} />
      </div>

      {/* Additional Information */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">📊 Analytics</h3>
          <p className="text-sm text-blue-700">
            View detailed analytics and reporting for better business insights
          </p>
          <Button variant="outline" size="sm" className="mt-2">
            View Analytics
          </Button>
        </div>

        <div className="bg-green-50 p-4 rounded-lg">
          <h3 className="font-semibold text-green-900 mb-2">💰 Revenue</h3>
          <p className="text-sm text-green-700">
            Track revenue streams and financial performance across all services
          </p>
          <Button variant="outline" size="sm" className="mt-2">
            View Reports
          </Button>
        </div>

        <div className="bg-purple-50 p-4 rounded-lg">
          <h3 className="font-semibold text-purple-900 mb-2">👥 Players</h3>
          <p className="text-sm text-purple-700">
            Manage player relationships and engagement analytics
          </p>
          <Button variant="outline" size="sm" className="mt-2">
            View Players
          </Button>
        </div>
      </div>
    </div>
  );
}