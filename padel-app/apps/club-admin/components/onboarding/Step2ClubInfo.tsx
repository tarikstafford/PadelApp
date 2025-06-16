"use client";

import { useState } from "react";
import { createClub } from "@/lib/api";
import { setCookie } from "cookies-next";
import { ClubForm, ClubFormValues } from "@/components/forms/ClubForm";
import { Button } from "@workspace/ui/components/button";

interface Step2Props {
  nextStep: () => void;
  prevStep: () => void;
  updateFormData: (data: any) => void;
  formData: any;
}

export default function Step2ClubInfo({ nextStep, prevStep, updateFormData, formData }: Step2Props) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(values: ClubFormValues) {
    setIsSubmitting(true);
    try {
      // The user's access token should have been stored in the shared formData from the previous step
      const token = formData.access_token;
      if (!token) {
        // Handle missing token case, maybe redirect to login or show an error
        console.error("Authentication token is missing from form data.");
        // Optionally, show a toast to the user.
        setIsSubmitting(false);
        return;
      }

      const newClub = await createClub(values, token);
      updateFormData({ ...values, clubId: newClub.id });
      // We might not need this cookie if middleware isn't using it anymore, but it doesn't hurt.
      setCookie("clubId", String(newClub.id)); 
      nextStep();
    } catch (error) {
      // Error is already handled and shown as a toast by apiClient
      console.error("Failed to create club during onboarding:", error);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <>
      <h1 className="text-2xl font-bold text-center mb-8">Tell Us About Your Club</h1>
      <ClubForm
        onSubmit={onSubmit}
        defaultValues={formData}
        isSubmitting={isSubmitting}
        submitButtonText="Next"
      />
      <div className="mt-4">
        <Button
          type="button"
          variant="outline"
          onClick={prevStep}
          disabled={isSubmitting}
          className="w-full"
        >
          Back
        </Button>
      </div>
    </>
  );
} 