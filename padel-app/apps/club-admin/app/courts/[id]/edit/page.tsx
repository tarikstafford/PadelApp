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
import { Checkbox } from "@workspace/ui/components/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@workspace/ui/components/select";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter, useParams } from "next/navigation";
import { useEffect } from "react";
import { apiClient } from "@/lib/api";
import { Court } from "@/lib/types";
import { toast } from "sonner";

const formSchema = z.object({
  name: z.string().min(1, { message: "Court name is required" }),
  surface_type: z.string().optional(),
  is_indoor: z.boolean().optional(),
  price_per_hour: z.number().optional(),
  default_availability_status: z.string().optional(),
});

export default function EditCourtPage() {
  const { user } = useAuth();
  const router = useRouter();
  const params = useParams();
  const { id } = params;

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  });

  useEffect(() => {
    if (user && id) {
      apiClient.get<Court>(`/admin/my-club/courts/${id}`)
        .then(data => {
          form.reset(data);
        })
        .catch(error => {
          console.error("Failed to fetch court data", error);
        });
    }
  }, [user, id, form]);

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      await apiClient.put(`/admin/my-club/courts/${id}`, values);
      toast.success("Court updated successfully!");
      router.push("/courts");
    } catch (error) {
      toast.error("Failed to update court. Please try again.");
      console.error("Update court failed", error);
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Edit Court</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Court Name</FormLabel>
                <FormControl>
                  <Input placeholder="Court 1" {...field} />
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
                <Select onValueChange={field.onChange} defaultValue={field.value}>
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
                  <Input type="number" placeholder="25" {...field} onChange={event => field.onChange(+event.target.value)} />
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
                <Select onValueChange={field.onChange} defaultValue={field.value}>
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
          <Button type="submit">Save Changes</Button>
        </form>
      </Form>
    </div>
  );
} 