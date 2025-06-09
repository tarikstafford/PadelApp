"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { apiClient } from "@/lib/api";
import { Club } from "@/lib/types";
import { CreateClubForm } from "@/components/onboarding/CreateClubForm";
import { EditClubForm } from "@/components/onboarding/EditClubForm";

export default function ProfilePage() {
  const { user } = useAuth();
  const [club, setClub] = useState<Club | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      apiClient.get<Club>("/admin/my-club")
        .then(data => {
          setClub(data);
          setLoading(false);
        })
        .catch(error => {
          console.error("Failed to fetch club data", error);
          setLoading(false);
        });
    }
  }, [user]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      {club ? <EditClubForm club={club} /> : <CreateClubForm />}
    </div>
  );
} 