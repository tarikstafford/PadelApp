"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { apiClient } from "@/lib/api";
import { EloAdjustmentRequest } from "@/lib/types";
import { Avatar, AvatarFallback, AvatarImage } from "@workspace/ui/components/avatar";
import { EloAdjustmentRequestModal } from "@/components/profile/EloAdjustmentRequestModal";
import { EloRatingDisplay } from "@/components/profile/EloRatingDisplay";
import { PreferredPositionSelection } from "@/components/profile/PreferredPositionSelection";
import { EloAdjustmentRequestHistory } from "@/components/profile/EloAdjustmentRequestHistory";

export default function ProfilePage() {
  const { user } = useAuth();
  const [requests, setRequests] = useState<EloAdjustmentRequest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      apiClient
        .get<EloAdjustmentRequest[]>("/users/me/elo-adjustment-requests")
        .then((data) => {
          setRequests(data);
        })
        .catch((error) => {
          console.error("Failed to fetch ELO adjustment requests", error);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [user]);

  const canMakeRequest = () => {
    if (requests.some(req => req.status === 'pending')) {
      return false;
    }
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    const recentRequest = requests.find(req => new Date(req.created_at) > thirtyDaysAgo);
    return !recentRequest;
  };

  if (!user || loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex items-center space-x-4 mb-8">
        <Avatar className="h-24 w-24">
          <AvatarImage src={user.profile_picture_url || undefined} />
          <AvatarFallback>{user.full_name?.substring(0, 2)}</AvatarFallback>
        </Avatar>
        <div>
          <h1 className="text-3xl font-bold">{user.full_name}</h1>
          <p className="text-gray-500">{user.email}</p>
        </div>
      </div>

      <div className="space-y-8">
        <div>
          <h2 className="text-xl font-bold mb-4">Padel Details</h2>
          <div className="space-y-4">
            <EloRatingDisplay eloRating={user.elo_rating} />
            <div>
              <h3 className="text-lg font-bold">Preferred Position</h3>
              <PreferredPositionSelection />
            </div>
            <EloAdjustmentRequestModal canMakeRequest={canMakeRequest()} />
          </div>
        </div>
        <EloAdjustmentRequestHistory requests={requests} loading={loading} />
      </div>
    </div>
  );
} 