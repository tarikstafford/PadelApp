"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the new admin dashboard
    router.replace("/admin");
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p>Redirecting to enhanced dashboard...</p>
      </div>
    </div>
  );
}