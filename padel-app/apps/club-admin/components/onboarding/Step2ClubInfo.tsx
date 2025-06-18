"use client";

import { useState, useRef } from "react";
import { createClub } from "@/lib/api";
import { setCookie } from "cookies-next";
import { ClubForm, ClubFormValues } from "@/components/forms/ClubForm";
import { Button } from "@workspace/ui/components/button";
import { UseFormReturn } from "react-hook-form";

interface Step2Props {
  nextStep: () => void;
  prevStep: () => void;
  updateFormData: (data: any) => void;
  formData: any;
}

export default function Step2ClubInfo({ nextStep, prevStep, updateFormData, formData }: Step2Props) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const formRef = useRef<UseFormReturn<ClubFormValues>>(null);

  // We need a way to check validity for the button state
  const [isFormValid, setIsFormValid] = useState(false);

  // This is a bit of a hack to get the form state. 
  // RHF doesn't make it easy to subscribe to state changes outside the form component.
  // A better solution might involve a shared state manager (context/zustand) for the form state.
  // For now, let's poll it, but this is not ideal.
  // Let's go back to the onValidationChange idea, it was better.
  // I will revert the previous change and re-implement the onValidationChange solution, but correctly this time.
  // The assistant's last attempt was flawed.

  async function onSubmit(values: ClubFormValues) {
    setIsSubmitting(true);
    try {
      const token = formData.access_token;
      if (!token) {
        console.error("Authentication token is missing from form data.");
        setIsSubmitting(false);
        return;
      }

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

      const newClub = await createClub(dataToSend, token);
      updateFormData({ ...values, clubId: newClub.id });
      setCookie("clubId", String(newClub.id)); 
      nextStep();
    } catch (error) {
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
        onValidationChange={setIsFormValid}
      >
        <div className="mt-4 flex flex-col space-y-2">
          <Button
            type="submit"
            disabled={!isFormValid || isSubmitting}
            className="w-full"
          >
            {isSubmitting ? "Saving..." : "Next"}
          </Button>
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
      </ClubForm>
    </>
  );
} 