"use client";

import { useState } from "react";
import Step1Account from "@/components/onboarding/Step1Account";
import Step2ClubInfo from "@/components/onboarding/Step2ClubInfo";
import Step3Confirm from "@/components/onboarding/Step3Confirm";

export default function RegisterPage() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    admin_name: "",
    admin_email: "",
    admin_password: "",
    name: "",
    address: "",
    city: "",
  });

  const nextStep = () => setStep((prev) => prev + 1);
  const prevStep = () => setStep((prev) => prev - 1);

  const updateFormData = (data: any) => {
    setFormData((prev) => ({ ...prev, ...data }));
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return <Step1Account nextStep={nextStep} updateFormData={updateFormData} formData={formData} />;
      case 2:
        return <Step2ClubInfo nextStep={nextStep} prevStep={prevStep} updateFormData={updateFormData} formData={formData} />;
      case 3:
        return <Step3Confirm prevStep={prevStep} formData={formData} />;
      default:
        return <Step1Account nextStep={nextStep} updateFormData={updateFormData} formData={formData} />;
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md">
        {renderStep()}
      </div>
    </div>
  );
} 