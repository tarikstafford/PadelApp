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
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";

const formSchema = z.object({
  name: z.string().min(1, { message: "Court name is required" }),
  surface_type: z.string().optional(),
  is_indoor: z.boolean().optional(),
  price_per_hour: z.number().optional(),
  default_availability_status: z.string().optional(),
});

export default function NewCourtPage() {
  const { user } = useAuth();
  const router = useRouter();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      surface_type: "",
      is_indoor: false,
      price_per_hour: 0,
      default_availability_status: "Available",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      await apiClient.post("/admin/my-club/courts", values);
      toast.success("Court created successfully!");
      router.push("/courts");
    } catch (error) {
      toast.error("Failed to create court. Please try again.");
      console.error("Create court failed", error);
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Add New Court</h1>
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
                    <SelectItem value="Clay">Clay</SelectItem>
                    <SelectItem value="Hard">Hard</SelectItem>
                    <SelectItem value="Grass">Grass</SelectItem>
                    <SelectItem value="Artificial Grass">Artificial Grass</SelectItem>
                    <SelectItem value="Artificial Grass Pro">Artificial Grass Pro</SelectItem>
                    <SelectItem value="Panoramic Glass">Panoramic Glass</SelectItem>
                    <SelectItem value="ConcreteTextured">Concrete Textured</SelectItem>
                    <SelectItem value="Cushioned Hard Court">Cushioned Hard Court</SelectItem>
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
          <Button type="submit">Create Court</Button>
        </form>
      </Form>
    </div>
  );
} 