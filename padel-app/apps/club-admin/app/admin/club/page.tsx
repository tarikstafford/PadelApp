"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

export default function ClubProfilePage() {
  const router = useRouter();
  const { user } = useAuth();

  useEffect(() => {
    // This logic needs to be updated to get the actual club ID
    // for the currently authenticated admin.
    const clubId = user ? 1 : null; 
    if (clubId) {
      router.push(`/admin/club/${clubId}/edit`); // Redirect to a future edit page
    }
  }, [user, router]);

  return (
    <div>
      <h1 className="text-3xl font-bold">Club Profile</h1>
      <p>Redirecting to your club&apos;s profile...</p>
    </div>
  );
} 