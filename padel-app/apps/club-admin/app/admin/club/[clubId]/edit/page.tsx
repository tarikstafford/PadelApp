"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@workspace/ui/components/form";
import { Input } from "@workspace/ui/components/input";
import { Button } from "@workspace/ui/components/button";
import { useClubDetails } from "@/hooks/useClubDetails";
import { updateClub } from "@/lib/api";
import { useParams, useRouter } from "next/navigation";
import { useEffect } from "react";

const formSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters."),
  address: z.string().optional(),
  city: z.string().optional(),
  postal_code: z.string().optional(),
  phone: z.string().optional(),
  email: z.string().email("Invalid email address.").optional(),
});

export default function ClubEditPage() {
  const router = useRouter();
  const params = useParams();
  const clubId = Number(params.clubId);
  const { data: club, isLoading, error } = useClubDetails(clubId);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      address: "",
      city: "",
      postal_code: "",
      phone: "",
      email: "",
    },
  });

  useEffect(() => {
    if (club) {
      form.reset(club);
    }
  }, [club, form]);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    await updateClub(clubId, values);
    router.push("/admin/club");
  };

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Failed to load club details.</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Edit Club Profile</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
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
                  <Input placeholder="123 Main St" {...field} />
                </FormControl>
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