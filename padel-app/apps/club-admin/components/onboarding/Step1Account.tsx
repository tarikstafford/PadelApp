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
import { registerAdmin } from "@/lib/api";
import { setCookie } from "cookies-next";

const formSchema = z.object({
  full_name: z.string().min(1, { message: "Name is required" }),
  email: z.string().email(),
  password: z.string().min(8, { message: "Password must be at least 8 characters" }),
});

interface Step1Props {
  nextStep: () => void;
  updateFormData: (data: Record<string, unknown>) => void;
  formData: Record<string, unknown>;
}

export default function Step1Account({ nextStep, updateFormData, formData }: Step1Props) {
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      full_name: String(formData.full_name || ""),
      email: String(formData.email || ""),
      password: String(formData.password || ""),
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsLoading(true);
    try {
      const { access_token, refresh_token, role } = await registerAdmin({
        full_name: values.full_name,
        email: values.email,
        password: values.password,
      });
      
      setCookie("token", access_token);
      setCookie("refresh_token", refresh_token);
      
      updateFormData({ ...values, role, access_token, refresh_token });
      nextStep();
    } catch {
      // Error is already handled by apiClient, which shows a toast
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <>
      <h1 className="text-2xl font-bold text-center mb-8">Create Your Account</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="full_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Your Name</FormLabel>
                <FormControl>
                  <Input placeholder="John Doe" {...field} disabled={isLoading} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Your Email</FormLabel>
                <FormControl>
                  <Input placeholder="email@example.com" {...field} disabled={isLoading} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Password</FormLabel>
                <FormControl>
                  <Input type="password" placeholder="********" {...field} disabled={isLoading} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Creating Account..." : "Next"}
          </Button>
        </form>
      </Form>
    </>
  );
} 