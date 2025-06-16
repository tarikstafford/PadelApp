"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { apiClient } from "@/lib/api";
import { Club } from "@/lib/types"; // Assuming a Club type is defined in types.ts
import { Button } from "@workspace/ui/components/button";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";

export default function DashboardPage() {
  const { user } = useAuth();
  const [club, setClub] = useState<Club | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // The middleware now handles redirecting users without a club.
    // This component will only fetch data if the user is allowed to be here.
    if (user) {
      const fetchClubData = async () => {
        try {
          const data = await apiClient.get<Club>("/admin/my-club", { silenceError: true });
          setClub(data);
        } catch (error: any) {
          // Errors are handled by the apiClient. If we get here, it's likely a 404.
          setClub(null);
        } finally {
          setLoading(false);
        }
      };
      fetchClubData();
    } else if (!user && !loading) {
      router.push('/login');
    }
  }, [user, loading, router]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!club) {
    // This should theoretically not be reached if the middleware is working correctly
    // for users without a club. This can serve as a fallback UI.
    return (
      <div className="flex flex-col items-center justify-center text-center p-8">
        <h2 className="text-2xl font-bold mb-2">Welcome!</h2>
        <p className="mb-4 text-gray-600">Let's get your club set up.</p>
        <Button asChild>
          <Link href="/admin/club/new/edit">Create Your Club Profile</Link>
        </Button>
      </div>
    );
  }

  return (
    <Link href={`/admin/club/${club.id}/edit`} className="block hover:bg-gray-50">
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">{club.name}</h1>
        <p>{club.address}</p>
        <p>{club.city}, {club.postal_code}</p>
        <p>{club.phone}</p>
        <p>{club.email}</p>
        <p>{club.description}</p>
      </div>
    </Link>
  );
} 