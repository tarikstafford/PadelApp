"use client";

import { Button } from "@workspace/ui/components/button";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

interface Step3Props {
  prevStep: () => void;
  formData: any;
}

export default function Step3Confirm({ prevStep, formData }: Step3Props) {
  const { register } = useAuth();
  const router = useRouter();

  const handleSubmit = async () => {
    try {
      await register(formData);
      toast.success("Registration successful!");
      router.push("/dashboard");
    } catch (error) {
      toast.error("Registration failed. Please try again.");
      console.error("Registration failed", error);
    }
  };

  return (
    <>
      <h1 className="text-2xl font-bold text-center mb-8">Confirm Your Details</h1>
      <div className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold">Account Details</h2>
          <p>Name: {formData.admin_name}</p>
          <p>Email: {formData.admin_email}</p>
        </div>
        <div>
          <h2 className="text-lg font-semibold">Club Details</h2>
          <p>Name: {formData.name}</p>
          <p>Address: {formData.address}</p>
          <p>City: {formData.city}</p>
        </div>
      </div>
      <div className="flex justify-between mt-8">
        <Button type="button" variant="outline" onClick={prevStep}>
          Back
        </Button>
        <Button onClick={handleSubmit}>Complete Registration</Button>
      </div>
    </>
  );
} 