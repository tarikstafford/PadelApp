"use client";

import { RegistrationFormProvider } from "@/contexts/RegistrationFormContext";
import MultiStepForm from "@/components/onboarding/MultiStepForm";

export default function RegisterPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <RegistrationFormProvider>
        <MultiStepForm />
      </RegistrationFormProvider>
    </div>
  );
} 