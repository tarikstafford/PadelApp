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
import { toast } from "sonner";
import { Input } from "@workspace/ui/components/input";

export default function CourtsPage() {
  const { user } = useAuth();
  const [courts, setCourts] = useState<Court[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

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

  const handleDeleteCourt = async (courtId: number) => {
    try {
      await apiClient.delete(`/admin/my-club/courts/${courtId}`);
      setCourts(courts.filter(court => court.id !== courtId));
      toast.success("Court deleted successfully!");
    } catch (error) {
      toast.error("Failed to delete court. Please try again.");
      console.error("Delete court failed", error);
    }
  };

  const filteredCourts = courts.filter(court =>
    court.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Courts</h1>
        <div className="flex items-center space-x-2">
          <Input
            placeholder="Filter by name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-64"
          />
          <Button asChild>
            <Link href="/courts/new">Add New Court</Link>
          </Button>
        </div>
      </div>
      {courts.length === 0 ? (
        <div className="flex flex-col items-center justify-center text-center p-8 border-dashed border-2 rounded-lg mt-8">
          <h2 className="text-xl font-semibold mb-2">No Courts Found</h2>
          <p className="mb-4 text-gray-600">Get started by adding your first court.</p>
          <Button asChild>
            <Link href="/courts/new">Add Your First Court</Link>
          </Button>
        </div>
      ) : (
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
            {filteredCourts.map((court) => (
              <TableRow key={court.id}>
                <TableCell>{court.name}</TableCell>
                <TableCell>{court.surface_type}</TableCell>
                <TableCell>{court.is_indoor ? "Indoor" : "Outdoor"}</TableCell>
                <TableCell>${court.price_per_hour}</TableCell>
                <TableCell>{court.default_availability_status}</TableCell>
                <TableCell>
                  <Button asChild variant="outline" className="mr-2">
                    <Link href={`/courts/${court.id}/edit`}>Edit</Link>
                  </Button>
                  <Button variant="destructive" onClick={() => handleDeleteCourt(court.id)}>Delete</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
} 