"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { apiClient } from "@/lib/api";
import { Club } from "@/lib/types"; // Assuming a Club type is defined in types.ts
import { Button } from "@workspace/ui/components/button";
import Link from "next/link";

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
    return (
      <div className="flex flex-col items-center justify-center text-center p-8">
        <h2 className="text-2xl font-bold mb-2">Welcome to Your Dashboard!</h2>
        <p className="mb-4 text-gray-600">It looks like you haven't created a club yet. Let's get started.</p>
        <Button asChild>
          <Link href="/profile">Create Your Club Profile</Link>
        </Button>
      </div>
    );
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