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
  name: z.string().min(1, { message: "Club name is required" }),
  address: z.string().optional(),
  city: z.string().optional(),
});

interface Step2Props {
  nextStep: () => void;
  prevStep: () => void;
  updateFormData: (data: any) => void;
  formData: any;
}

export default function Step2ClubInfo({ nextStep, prevStep, updateFormData, formData }: Step2Props) {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: formData.name,
      address: formData.address,
      city: formData.city,
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    updateFormData(values);
    nextStep();
  }

  return (
    <>
      <h1 className="text-2xl font-bold text-center mb-8">Tell Us About Your Club</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Club Name</FormLabel>
                <FormControl>
                  <Input placeholder="Padel Club" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="address"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Address</FormLabel>
                <FormControl>
                  <Input placeholder="123 Padel St" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="city"
            render={({ field }) => (
              <FormItem>
                <FormLabel>City</FormLabel>
                <FormControl>
                  <Input placeholder="Padelville" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="flex justify-between">
            <Button type="button" variant="outline" onClick={prevStep}>
              Back
            </Button>
            <Button type="submit">Next</Button>
          </div>
        </form>
      </Form>
    </>
  );
} 