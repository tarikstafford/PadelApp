"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@workspace/ui/components/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@workspace/ui/components/form";
import { Input } from "@workspace/ui/components/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@workspace/ui/components/card";
import { OperationalHoursSelector } from "@/components/shared/OperationalHoursSelector";
import { ImageUploader } from "@/components/shared/ImageUploader";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";
import { Club } from "@/lib/types";
import { useRouter } from "next/navigation";
import { getCookie } from "cookies-next";

const clubFormSchema = z.object({
  name: z.string().min(2, "Club name must be at least 2 characters"),
  description: z.string().optional(),
  address: z.string().min(5, "Address is required"),
  city: z.string().min(2, "City is required"),
  postal_code: z.string().min(5, "Zip code is required"),
  phone: z.string().optional(),
  email: z.string().email("Invalid email address").optional(),
  website: z.string().url("Invalid website URL").optional(),
  operationalHours: z.any(),
});

type ClubFormValues = z.infer<typeof clubFormSchema>;

export function EditClubForm({ club }: { club: Club }) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  const form = useForm<ClubFormValues>({
    resolver: zodResolver(clubFormSchema),
    defaultValues: {
      name: club.name || "",
      description: club.description || "",
      address: club.address || "",
      city: club.city || "",
      postal_code: club.postal_code || "",
      phone: club.phone || "",
      email: club.email || "",
      website: club.website || "",
      operationalHours: club.operationalHours || {
        monday: null, tuesday: null, wednesday: null, thursday: null, friday: null, saturday: null, sunday: null,
      },
    },
  });

  const handleImageUpload = async (file: File | null) => {
    if (!file) return;

    toast.info("Uploading new image...");
    const token = getCookie("token");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${apiBaseUrl}/api/v1/admin/my-club/profile-picture`, {
        method: "POST",
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Image upload failed.");
      
      toast.success("Image updated successfully!");
      // Force a reload to show the new image
      router.refresh();

    } catch (error: any) {
      toast.error(error.message || "Failed to upload image.");
      console.error(error);
    }
  };
  
  const handleSubmit = async (values: ClubFormValues) => {
    setIsSubmitting(true);
    try {
      await apiClient.put("/admin/my-club", values);
      toast.success("Club updated successfully!");
    } catch (error) {
      console.error("Error updating club:", error);
      toast.error("There was a problem updating your club");
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <Card className="w-full max-w-3xl mx-auto">
      <CardHeader>
        <CardTitle>Edit Your Club</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4 mb-8">
            <FormLabel>Club Image</FormLabel>
            {club.image_url && (
              <div className="w-full h-48 rounded-md overflow-hidden bg-muted">
                  <img 
                    src={`${process.env.NEXT_PUBLIC_API_BASE_URL}${club.image_url}`}
                    alt="Current club image" 
                    className="w-full h-full object-cover"
                  />
              </div>
            )}
            <ImageUploader onFileSelect={handleImageUpload} label="Upload New Image" />
        </div>
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Club Name*</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter club name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="phone"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Phone Number</FormLabel>
                    <FormControl>
                      <Input placeholder="(555) 555-5555" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea 
                      placeholder="Brief description of your club" 
                      className="min-h-[100px]" 
                      {...field} 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="address"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Address*</FormLabel>
                    <FormControl>
                      <Input placeholder="Street address" {...field} />
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
                    <FormLabel>City*</FormLabel>
                    <FormControl>
                      <Input placeholder="City" {...field} />
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
                    <FormLabel>Zip Code*</FormLabel>
                    <FormControl>
                      <Input placeholder="Zip code" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input placeholder="contact@example.com" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="website"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Website</FormLabel>
                    <FormControl>
                      <Input placeholder="https://www.example.com" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="operationalHours"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <OperationalHoursSelector 
                        value={field.value || {
                          monday: null, tuesday: null, wednesday: null, thursday: null, friday: null, saturday: null, sunday: null,
                        }} 
                        onChange={field.onChange} 
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <CardFooter className="px-0 pt-4">
              <Button type="submit" disabled={isSubmitting} className="ml-auto">
                {isSubmitting ? "Saving..." : "Update Club"}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
} 