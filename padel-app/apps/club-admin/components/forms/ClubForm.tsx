"use client";

import React, { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@workspace/ui/components/form";
import { Input } from "@workspace/ui/components/input";
import { Textarea } from "@workspace/ui/components/textarea";
import ImageUploader from "../ImageUploader";

// This schema can be exported and reused if needed elsewhere
export const clubFormSchema = z.object({
  name: z.string().min(1, { message: "Club name is required" }),
  address: z.string().optional(),
  city: z.string().optional(),
  postal_code: z.string().optional(),
  phone: z.string().optional(),
  email: z.string().email({ message: "Invalid email address." }).optional().or(z.literal('')),
  description: z.string().optional(),
  opening_time: z.string().optional(),
  closing_time: z.string().optional(),
  amenities: z.string().optional(),
  image_url: z.string().optional(),
  image_file: z.any().optional(),
});

// Use refine on the client-side to ensure it's a file
// if (typeof window !== "undefined") {
//   clubFormSchema = clubFormSchema.refine(
//     (data) => {
//       if (data.image_file && !(data.image_file instanceof File)) {
//         return false;
//       }
//       return true;
//     },
//     {
//       message: "Image must be a valid file.",
//       path: ["image_file"],
//     }
//   );
// }

export type ClubFormValues = z.infer<typeof clubFormSchema>;

interface ClubFormProps {
  onSubmit: (values: ClubFormValues) => void;
  defaultValues?: Partial<ClubFormValues>;
  isSubmitting: boolean;
  onValidationChange: (isValid: boolean) => void;
  children: React.ReactNode; // For action buttons
}

export function ClubForm({ 
  onSubmit, 
  defaultValues = {},
  isSubmitting,
  onValidationChange,
  children,
}: ClubFormProps) {
  const form = useForm<ClubFormValues>({
    resolver: zodResolver(clubFormSchema),
    defaultValues: {
      name: "",
      address: "",
      city: "",
      postal_code: "",
      phone: "",
      email: "",
      description: "",
      opening_time: "",
      closing_time: "",
      amenities: "",
      image_url: "",
      ...defaultValues,
    },
    mode: 'onChange',
  });

  const { formState: { isValid } } = form;

  useEffect(() => {
    onValidationChange(isValid);
  }, [isValid, onValidationChange]);

  // This allows the form to be reset when the defaultValues prop changes (e.g., data loads)
  React.useEffect(() => {
    form.reset(defaultValues);
  }, [defaultValues, form]);

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Club Name</FormLabel>
              <FormControl>
                <Input placeholder="Padel Club" {...field} disabled={isSubmitting} />
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
                <Input placeholder="123 Padel St" {...field} disabled={isSubmitting} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="city"
            render={({ field }) => (
              <FormItem>
                <FormLabel>City</FormLabel>
                <FormControl>
                  <Input placeholder="Padelville" {...field} disabled={isSubmitting} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="postal_code"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Postal Code</FormLabel>
                <FormControl>
                  <Input placeholder="12345" {...field} disabled={isSubmitting} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        <FormField
          control={form.control}
          name="phone"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Phone Number</FormLabel>
              <FormControl>
                <Input placeholder="(123) 456-7890" {...field} disabled={isSubmitting} />
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
              <FormLabel>Club Email</FormLabel>
              <FormControl>
                <Input placeholder="contact@padelclub.com" {...field} disabled={isSubmitting} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Tell us a little bit about your club"
                  className="resize-none"
                  {...field}
                  disabled={isSubmitting}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="opening_time"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Opening Time</FormLabel>
                <FormControl>
                  <Input type="time" {...field} disabled={isSubmitting} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="closing_time"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Closing Time</FormLabel>
                <FormControl>
                  <Input type="time" {...field} disabled={isSubmitting} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        <FormField
          control={form.control}
          name="amenities"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Amenities</FormLabel>
              <FormControl>
                <Input placeholder="e.g., Wifi, Showers, Pro Shop" {...field} disabled={isSubmitting} />
              </FormControl>
              <FormDescription>
                Enter a comma-separated list of amenities.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="image_file"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <ImageUploader 
                  onFileChange={(file) => field.onChange(file)}
                  defaultImageUrl={form.getValues("image_url")}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {children}
      </form>
    </Form>
  );
} 