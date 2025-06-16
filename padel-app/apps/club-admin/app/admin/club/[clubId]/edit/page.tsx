"use client";

import { createClub, updateClub } from "@/lib/api";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { getCookie } from "cookies-next";
import { useClubDetails } from "@/hooks/useClubDetails";
import { ClubForm, ClubFormValues } from "@/components/forms/ClubForm";

export default function ClubEditPage() {
  const router = useRouter();
  const params = useParams();
  
  const clubIdOrNew = params.clubId as string;
  const isCreateMode = clubIdOrNew === "new";
  const clubId = isCreateMode ? null : Number(clubIdOrNew);

  const { data: club, isLoading, error } = useClubDetails(clubId);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const onSubmit = async (values: ClubFormValues) => {
    setIsSubmitting(true);
    try {
      if (isCreateMode) {
        const token = getCookie("token");
        if (!token) throw new Error("Authentication token is missing.");
        await createClub({ ...values }, token);
        // On success, you might want to show a toast and then redirect
        router.push(`/dashboard`);
      } else if (clubId) {
        await updateClub(clubId, values);
        // On success, you might want to show a toast and then redirect
        router.push(`/dashboard`);
      }
    } catch (err: any) {
      console.error("Failed to save club. Server response:", JSON.stringify(err, null, 2));
      // Error toast is likely handled by the apiClient, but you could add specific ones here
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) return <p>Loading...</p>;
  if (error && !isCreateMode) return <p>Failed to load club details.</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">
        {isCreateMode ? "Create Your Club Profile" : "Edit Club Profile"}
      </h1>
      <ClubForm
        onSubmit={onSubmit}
        defaultValues={club || {}}
        isSubmitting={isSubmitting}
        submitButtonText={isCreateMode ? "Create Club" : "Save Changes"}
      />
    </div>
  );
} 