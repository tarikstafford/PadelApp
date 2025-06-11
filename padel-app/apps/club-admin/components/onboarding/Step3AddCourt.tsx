"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@workspace/ui/components/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@workspace/ui/components/form";
import { Input } from "@workspace/ui/components/input";
import { createCourt } from "@/lib/api";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

const formSchema = z.object({
  name: z.string().min(1, { message: "Court name is required" }),
  surface_type: z.string().optional(),
});

interface Step3Props {
  prevStep: () => void;
  formData: any;
}

export default function Step3AddCourt({ prevStep, formData }: Step3Props) {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsLoading(true);
    try {
      await createCourt(values);
      toast.success("Club and initial court created successfully!");
      router.push("/dashboard");
    } catch (error) {
      // Error is handled by apiClient
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <>
      <h1 className="text-2xl font-bold text-center mb-8">Add Your First Court</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Court Name</FormLabel>
                <FormControl>
                  <Input placeholder="Center Court" {...field} disabled={isLoading} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="surface_type"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Surface Type (e.g., Turf, Clay)</FormLabel>
                <FormControl>
                  <Input placeholder="Turf" {...field} disabled={isLoading} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="flex justify-between pt-4">
            <Button type="button" variant="outline" onClick={prevStep} disabled={isLoading}>
              Back
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Finishing..." : "Complete Registration"}
            </Button>
          </div>
        </form>
      </Form>
    </>
  );
} 