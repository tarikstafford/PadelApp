"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { apiClient } from "@/lib/api";
import { Club } from "@/lib/types";
import { CreateClubForm } from "@/components/onboarding/CreateClubForm";
import { EditClubForm } from "@/components/onboarding/EditClubForm";

export default function ProfilePage() {
  const { user, isLoading: isAuthLoading } = useAuth();
  const [club, setClub] = useState<Club | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      setLoading(true);
      apiClient.get<Club>("/admin/my-club")
        .then(data => {
          setClub(data);
        })
        .catch(error => {
          // If the error is a 404, it just means the club doesn't exist yet.
          // We can safely assume we should show the create form.
          if (error?.status !== 404) {
             console.error("Failed to fetch club data", error);
          }
          setClub(null);
        })
        .finally(() => {
          setLoading(false);
        });
    } else if (!isAuthLoading) {
      // If there's no user and auth is not loading, we can stop loading.
      setLoading(false);
    }
  }, [user, isAuthLoading]);

  if (loading || isAuthLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      {club ? <EditClubForm club={club} /> : <CreateClubForm />}
    </div>
  );
} 