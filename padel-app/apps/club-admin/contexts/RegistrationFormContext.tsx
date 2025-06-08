"use client";

import { createContext, useContext, useState, ReactNode } from "react";

interface FormData {
  admin_name: string;
  admin_email: string;
  admin_password: string;
  name: string;
  address: string;
  city: string;
}

interface RegistrationFormContextType {
  formData: FormData;
  currentStep: number;
  updateFormData: (data: Partial<FormData>) => void;
  nextStep: () => void;
  prevStep: () => void;
}

const RegistrationFormContext = createContext<RegistrationFormContextType | undefined>(undefined);

export function useRegistrationForm() {
  const context = useContext(RegistrationFormContext);
  if (context === undefined) {
    throw new Error("useRegistrationForm must be used within a RegistrationFormProvider");
  }
  return context;
}

export function RegistrationFormProvider({ children }: { children: ReactNode }) {
  const [formData, setFormData] = useState<FormData>({
    admin_name: "",
    admin_email: "",
    admin_password: "",
    name: "",
    address: "",
    city: "",
  });
  const [currentStep, setCurrentStep] = useState(1);

  const updateFormData = (data: Partial<FormData>) => {
    setFormData((prev) => ({ ...prev, ...data }));
  };

  const nextStep = () => setCurrentStep((prev) => prev + 1);
  const prevStep = () => setCurrentStep((prev) => prev - 1);

  const value = {
    formData,
    currentStep,
    updateFormData,
    nextStep,
    prevStep,
  };

  return (
    <RegistrationFormContext.Provider value={value}>
      {children}
    </RegistrationFormContext.Provider>
  )
} 