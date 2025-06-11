"use client";
import { RegistrationFormProvider } from "@/contexts/RegistrationFormContext";
import MultiStepForm from "@/components/onboarding/MultiStepForm";
import { Suspense } from "react";
import { useSearchParams } from "next/navigation";

// This is now a client component that wraps the form
function RegisterContent() {
  const searchParams = useSearchParams();
  const step = searchParams.get("step");
  const initialStep = step ? parseInt(step, 10) : 1;

  // This component no longer fetches data.
  // It relies on the provider to be pre-populated.
  return (
      <RegistrationFormProvider initialStep={initialStep}>
        <MultiStepForm />
      </RegistrationFormProvider>
  );
}

// This is the main page component which will be wrapped in Suspense
// Note: I'm reverting this to a client component and abandoning the server-side fetch
// as it is causing too many issues with the current setup.
// We will pre-populate the form on the client-side instead.
export default function RegisterPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <Suspense fallback={<div>Loading...</div>}>
        <RegisterContent />
      </Suspense>
    </div>
  );
} 