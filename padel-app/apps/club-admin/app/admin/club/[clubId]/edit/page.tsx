"use client";

import { createClub, updateClub } from "@/lib/api";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { getCookie } from "cookies-next";
import { useClubDetails } from "@/hooks/useClubDetails";
import { ClubForm, ClubFormValues } from "@/components/forms/ClubForm";
import { Button } from "@workspace/ui/components/button";

export default function ClubEditPage() {
  const router = useRouter();
  const params = useParams();
  
  const clubIdOrNew = params.clubId as string;
  const isCreateMode = clubIdOrNew === "new";
  const clubId = isCreateMode ? null : Number(clubIdOrNew);

  const { data: club, isLoading, error } = useClubDetails(clubId);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isFormValid, setIsFormValid] = useState(false);

  const onSubmit = async (values: ClubFormValues) => {
    setIsSubmitting(true);
    try {
      const clubData: any = { ...values };
      let dataToSend: ClubFormValues | FormData = clubData;

      if (clubData.image_file) {
        const formData = new FormData();
        Object.keys(clubData).forEach(key => {
          if (key === 'image_file' && clubData[key]) {
            formData.append(key, clubData[key]);
          } else if (clubData[key] !== null && clubData[key] !== undefined) {
            formData.append(key, clubData[key]);
          }
        });
        dataToSend = formData;
      }

      if (isCreateMode) {
        const token = getCookie("token");
        if (!token) throw new Error("Authentication token is missing.");
        await createClub(dataToSend, token);
        router.push(`/dashboard`);
      } else if (clubId) {
        await updateClub(clubId, dataToSend);
        router.push(`/dashboard`);
      }
    } catch (err: any) {
      console.error("Failed to save club. Server response:", JSON.stringify(err, null, 2));
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
        onValidationChange={setIsFormValid}
      >
        <Button
          type="submit"
          disabled={!isFormValid || isSubmitting}
          className="w-full"
        >
          {isSubmitting ? "Saving..." : (isCreateMode ? "Create Club" : "Save Changes")}
        </Button>
      </ClubForm>
    </div>
  );
} 