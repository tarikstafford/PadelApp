"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { apiClient } from "@/lib/api";
import { Club } from "@/lib/types"; // Assuming a Club type is defined in types.ts

export default function DashboardPage() {
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

  if (!club) {
    return <div>No club found for this admin.</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">{club.name}</h1>
      <p>{club.address}</p>
      <p>{club.city}, {club.postal_code}</p>
      <p>{club.phone}</p>
      <p>{club.email}</p>
      <p>{club.description}</p>
    </div>
  );
} 