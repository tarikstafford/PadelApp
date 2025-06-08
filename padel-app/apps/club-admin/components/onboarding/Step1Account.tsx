"use client";

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

const formSchema = z.object({
  admin_name: z.string().min(1, { message: "Name is required" }),
  admin_email: z.string().email(),
  admin_password: z.string().min(8, { message: "Password must be at least 8 characters" }),
});

interface Step1Props {
  nextStep: () => void;
  updateFormData: (data: any) => void;
  formData: any;
}

export default function Step1Account({ nextStep, updateFormData, formData }: Step1Props) {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      admin_name: formData.admin_name,
      admin_email: formData.admin_email,
      admin_password: formData.admin_password,
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    updateFormData(values);
    nextStep();
  }

  return (
    <>
      <h1 className="text-2xl font-bold text-center mb-8">Create Your Account</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="admin_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Your Name</FormLabel>
                <FormControl>
                  <Input placeholder="John Doe" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="admin_email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Your Email</FormLabel>
                <FormControl>
                  <Input placeholder="email@example.com" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="admin_password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Password</FormLabel>
                <FormControl>
                  <Input type="password" placeholder="********" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" className="w-full">Next</Button>
        </form>
      </Form>
    </>
  );
} 