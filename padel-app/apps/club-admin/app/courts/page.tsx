"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { apiClient } from "@/lib/api";
import { Court } from "@/lib/types";
import { Button } from "@workspace/ui/components/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@workspace/ui/components/table";
import Link from "next/link";

export default function CourtsPage() {
  const { user } = useAuth();
  const [courts, setCourts] = useState<Court[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      apiClient.get<Court[]>("/admin/my-club/courts")
        .then(data => {
          setCourts(data);
          setLoading(false);
        })
        .catch(error => {
          console.error("Failed to fetch courts data", error);
          setLoading(false);
        });
    }
  }, [user]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Courts</h1>
        <Button asChild>
          <Link href="/courts/new">Add New Court</Link>
        </Button>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Surface</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Price/Hour</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {courts.map((court) => (
            <TableRow key={court.id}>
              <TableCell>{court.name}</TableCell>
              <TableCell>{court.surface_type}</TableCell>
              <TableCell>{court.is_indoor ? "Indoor" : "Outdoor"}</TableCell>
              <TableCell>${court.price_per_hour}</TableCell>
              <TableCell>{court.default_availability_status}</TableCell>
              <TableCell>
                <Button asChild variant="outline">
                  <Link href={`/courts/${court.id}/edit`}>Edit</Link>
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
} 