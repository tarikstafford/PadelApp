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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@workspace/ui/components/select";
import { Checkbox } from "@workspace/ui/components/checkbox";
import { createCourt } from "@/lib/api";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

const formSchema = z.object({
  name: z.string().min(1, { message: "Court name is required" }),
  surface_type: z.string().optional(),
  is_indoor: z.boolean().optional(),
  price_per_hour: z.coerce.number().optional(),
  default_availability_status: z.string().optional(),
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
      surface_type: "Turf",
      is_indoor: false,
      price_per_hour: 25,
      default_availability_status: "Available",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsLoading(true);
    try {
      if (!formData.clubId) {
        toast.error("Could not find club information. Please go back.");
        setIsLoading(false);
        return;
      }
      await createCourt({ ...values, club_id: formData.clubId });
      toast.success("Onboarding complete! Welcome to your dashboard.");
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
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Court Name</FormLabel>
                <FormControl>
                  <Input placeholder="Court 1" {...field} disabled={isLoading} />
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
                <FormLabel>Surface Type</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value} disabled={isLoading}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a surface type" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="Turf">Turf</SelectItem>
                    <SelectItem value="Clay">Clay</SelectItem>
                    <SelectItem value="Hard Court">Hard Court</SelectItem>
                    <SelectItem value="Sand">Sand</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="is_indoor"
            render={({ field }) => (
              <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                <FormControl>
                  <Checkbox
                    checked={field.value}
                    onCheckedChange={field.onChange}
                    disabled={isLoading}
                  />
                </FormControl>
                <div className="space-y-1 leading-none">
                  <FormLabel>
                    Indoor
                  </FormLabel>
                </div>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="price_per_hour"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Price Per Hour</FormLabel>
                <FormControl>
                  <Input type="number" placeholder="25" {...field} onChange={event => field.onChange(+event.target.value)} disabled={isLoading} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="default_availability_status"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Default Availability Status</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value} disabled={isLoading}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a status" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="Available">Available</SelectItem>
                    <SelectItem value="Unavailable">Unavailable</SelectItem>
                    <SelectItem value="Maintenance">Maintenance</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="flex justify-between pt-4">
            <Button type="button" variant="outline" onClick={prevStep} disabled={isLoading}>
              Back
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Finishing..." : "Complete Onboarding"}
            </Button>
          </div>
        </form>
      </Form>
    </>
  );
} 