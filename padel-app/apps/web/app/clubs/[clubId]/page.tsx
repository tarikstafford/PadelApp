"use client";

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation'; // useParams to get clubId, useRouter for back navigation
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@workspace/ui/components/card";
import { Button } from "@workspace/ui/components/button";
import { Badge } from "@workspace/ui/components/badge";
import { Loader2, AlertTriangle, ArrowLeft, MapPin, Phone, Mail, Clock, Sun, Moon, List, LayoutGrid } from 'lucide-react'; // Added List, LayoutGrid
import { Separator } from '@workspace/ui/components/separator'; // For visual separation
import { ToggleGroup, ToggleGroupItem } from "@workspace/ui/components/toggle-group"; // Import ToggleGroup

// Interfaces matching backend schemas (ensure these are consistent)
interface Court {
  id: number;
  name: string;
  surface_type?: string | null;
  is_indoor?: boolean | null;
  price_per_hour?: string | null; // Assuming backend sends Decimal as string
  default_availability_status?: string | null;
}

interface ClubWithCourts {
  id: number;
  name: string;
  address?: string | null;
  city?: string | null;
  postal_code?: string | null;
  phone?: string | null;
  email?: string | null;
  description?: string | null;
  opening_hours?: string | null;
  amenities?: string | null; // Will parse this if it's a comma-separated string
  image_url?: string | null;
  courts: Court[];
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function ClubDetailPage() {
  const params = useParams();
  const router = useRouter();
  const clubId = params.clubId as string; // clubId from the route

  const [club, setClub] = useState<ClubWithCourts | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [courtViewMode, setCourtViewMode] = useState<'grid' | 'list'>('grid'); // State for view mode

  const fetchClubDetails = useCallback(async () => {
    if (!clubId) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/clubs/${clubId}`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to fetch club details" }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      const data: ClubWithCourts = await response.json();
      setClub(data);
    } catch (err: any) {
      console.error(`Error fetching club ${clubId} details:`, err);
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  }, [clubId]);

  useEffect(() => {
    fetchClubDetails();
  }, [fetchClubDetails]);

  const parseAmenities = (amenitiesString?: string | null): string[] => {
    if (!amenitiesString) return [];
    return amenitiesString.split(',').map(amenity => amenity.trim()).filter(Boolean);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[calc(100vh-200px)]">
        <Loader2 className="h-16 w-16 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] text-center px-4">
        <AlertTriangle className="h-12 w-12 text-destructive mb-3" />
        <h2 className="text-xl font-semibold text-destructive mb-2">Error loading club details</h2>
        <p className="text-sm text-muted-foreground mb-4">{error}</p>
        <Button variant="outline" onClick={() => router.push('/discover')}>Back to Discover</Button>
      </div>
    );
  }

  if (!club) {
    return (
      <div className="text-center py-10">
        <p className="text-xl text-muted-foreground">Club not found.</p>
        <Button variant="link" onClick={() => router.push('/discover')} className="mt-2">
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Discover
        </Button>
      </div>
    );
  }

  const amenitiesList = parseAmenities(club.amenities);

  return (
    <div className="space-y-8 max-w-4xl mx-auto py-8 px-4">
      <Button variant="outline" onClick={() => router.push('/discover')} className="mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Discover Clubs
      </Button>

      <Card className="overflow-hidden">
        {club.image_url && (
          <img 
            src={club.image_url} 
            alt={`Image of ${club.name}`}
            className="w-full h-64 md:h-80 object-cover"
          />
        )}
        <CardHeader className="pt-6">
          <CardTitle className="text-3xl md:text-4xl font-bold">{club.name}</CardTitle>
          <CardDescription className="text-lg text-muted-foreground">
            {club.address}{club.city && `, ${club.city}`}{club.postal_code && ` ${club.postal_code}`}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {club.description && <p className="text-foreground/90">{club.description}</p>}
          
          <Separator />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h3 className="text-xl font-semibold">Contact & Hours</h3>
              {club.phone && <p className="flex items-center text-sm"><Phone className="mr-2 h-4 w-4 text-muted-foreground" /> {club.phone}</p>}
              {club.email && <p className="flex items-center text-sm"><Mail className="mr-2 h-4 w-4 text-muted-foreground" /> {club.email}</p>}
              {club.opening_hours && <p className="flex items-center text-sm"><Clock className="mr-2 h-4 w-4 text-muted-foreground" /> {club.opening_hours}</p>}
            </div>
            
            {amenitiesList.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-xl font-semibold">Amenities</h3>
                <div className="flex flex-wrap gap-2">
                  {amenitiesList.map((amenity, index) => (
                    <Badge key={index} variant="secondary">{amenity}</Badge>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Map Placeholder - Subtask mentions map component */}
          <Separator />
          <div>
            <h3 className="text-xl font-semibold mb-3">Location</h3>
            <div className="bg-muted h-64 rounded-md flex items-center justify-center">
              <p className="text-muted-foreground">[Map Placeholder - e.g., Google Maps Embed or Static Map Image]</p>
            </div>
          </div>

          {club.courts && club.courts.length > 0 && (
            <>
              <Separator />
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-semibold">Courts at {club.name}</h3>
                  <ToggleGroup 
                    type="single" 
                    value={courtViewMode} 
                    onValueChange={(value: string) => {
                        if (value === 'list' || value === 'grid') setCourtViewMode(value as 'grid' | 'list');
                    }}
                    aria-label="Court view mode"
                  >
                    <ToggleGroupItem value="grid" aria-label="Grid view">
                      <LayoutGrid className="h-4 w-4" />
                    </ToggleGroupItem>
                    <ToggleGroupItem value="list" aria-label="List view">
                      <List className="h-4 w-4" />
                    </ToggleGroupItem>
                  </ToggleGroup>
                </div>

                {courtViewMode === 'grid' ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {club.courts.map((court) => (
                      <Card key={court.id} className="flex flex-col">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-lg">{court.name}</CardTitle>
                          {court.surface_type && <CardDescription>{court.surface_type}</CardDescription>}
                        </CardHeader>
                        <CardContent className="space-y-1 text-sm flex-grow">
                          <p className="flex items-center">
                            {court.is_indoor ? 
                              <><Moon className="mr-2 h-4 w-4 text-blue-500" /> Indoor</> : 
                              <><Sun className="mr-2 h-4 w-4 text-yellow-500" /> Outdoor</>}
                          </p>
                          {court.price_per_hour && <p>Price: ${court.price_per_hour}/hr</p>}
                          {court.default_availability_status && 
                            <p>Status: <Badge variant={court.default_availability_status === "Available" ? "default" : "outline"} className={court.default_availability_status === "Available" ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300" : "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-300"}>{court.default_availability_status}</Badge></p>}
                        </CardContent>
                        <CardFooter>
                          <Link href={`/book/${court.id}?clubName=${encodeURIComponent(club.name)}&courtName=${encodeURIComponent(court.name)}`} passHref legacyBehavior>
                            <Button asChild size="sm" className="w-full">
                              <a>Book Now</a>
                            </Button>
                          </Link>
                        </CardFooter>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-3">
                    {club.courts.map((court) => (
                      <Card key={court.id} className="p-4">
                        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2">
                          <div>
                            <h4 className="font-semibold text-md">{court.name}</h4>
                            <p className="text-xs text-muted-foreground">
                              {court.surface_type} - {court.is_indoor ? "Indoor" : "Outdoor"}
                            </p>
                          </div>
                          <div className="text-sm text-right space-y-1">
                            {court.price_per_hour && <p className="font-medium">${court.price_per_hour}/hr</p>}
                            {court.default_availability_status && 
                                <Badge variant={court.default_availability_status === "Available" ? "default" : "outline"} className={court.default_availability_status === "Available" ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300" : "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-300"}>{court.default_availability_status}</Badge>}
                          </div>
                        </div>
                        <div className="mt-3 text-right sm:text-left">
                          <Link href={`/book/${court.id}?clubName=${encodeURIComponent(club.name)}&courtName=${encodeURIComponent(court.name)}`} passHref legacyBehavior>
                            <Button asChild variant="outline" size="sm">
                                <a>Book Now</a>
                            </Button>
                          </Link>
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 