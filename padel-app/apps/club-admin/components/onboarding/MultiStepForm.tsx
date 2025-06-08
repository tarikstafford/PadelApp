"use client";

import { useRegistrationForm } from "@/contexts/RegistrationFormContext";
import Step1Account from "./Step1Account";
import Step2ClubInfo from "./Step2ClubInfo";
import Step3Confirm from "./Step3Confirm";
import ProgressIndicator from "./ProgressIndicator";

export default function MultiStepForm() {
  const { currentStep, formData, updateFormData, nextStep, prevStep } = useRegistrationForm();

  const renderStep = () => {
    switch (currentStep) {
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
    <div className="w-full max-w-md">
      <ProgressIndicator />
      {renderStep()}
    </div>
  );
} 