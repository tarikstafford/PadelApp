"use client";

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@workspace/ui/components/card";
import { Button } from "@workspace/ui/components/button";
import { Input } from "@workspace/ui/components/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@workspace/ui/components/select";
import { Loader2, AlertTriangle } from 'lucide-react'; // For loading and error icons

interface Club {
  id: number;
  name: string;
  address?: string | null;
  city?: string | null;
  postal_code?: string | null;
  phone?: string | null;
  email?: string | null;
  description?: string | null;
  opening_hours?: string | null;
  amenities?: string | null;
  image_url?: string | null;
  // courts: any[]; // Not fetching courts list in this view for brevity, use ClubWithCourts for detail page
}

const ITEMS_PER_PAGE = 6;

export default function DiscoverPage() {
  const [clubs, setClubs] = useState<Club[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [currentPage, setCurrentPage] = useState(1);
  const [hasNextPage, setHasNextPage] = useState(false);
  // totalClubs and totalPages would require backend to send total count, 
  // for now, we use hasNextPage determined by fetching one extra item.

  const [searchTermName, setSearchTermName] = useState("");
  const [searchTermCity, setSearchTermCity] = useState("");
  const [sortBy, setSortBy] = useState("name"); // Default sort: name
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc"); // Default order: asc

  const fetchClubs = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.append('skip', ((currentPage - 1) * ITEMS_PER_PAGE).toString());
      params.append('limit', (ITEMS_PER_PAGE + 1).toString()); // Fetch one extra to check for next page
      if (searchTermName) params.append('name', searchTermName);
      if (searchTermCity) params.append('city', searchTermCity);
      if (sortBy) params.append('sort_by', sortBy);
      if (sortOrder === 'desc') params.append('sort_desc', 'true');

      // console.log(`/api/v1/clubs?${params.toString()}`);
      const response = await fetch(`/api/v1/clubs?${params.toString()}`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to fetch clubs" }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      const data: Club[] = await response.json();
      
      if (data.length > ITEMS_PER_PAGE) {
        setHasNextPage(true);
        setClubs(data.slice(0, ITEMS_PER_PAGE));
      } else {
        setHasNextPage(false);
        setClubs(data);
      }
    } catch (err: any) {
      console.error("Error fetching clubs:", err);
      setError(err.message || "An unexpected error occurred.");
      setClubs([]); // Clear clubs on error
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, searchTermName, searchTermCity, sortBy, sortOrder]);

  useEffect(() => {
    fetchClubs();
  }, [fetchClubs]);

  const handleSearchNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTermName(e.target.value);
    setCurrentPage(1); // Reset to first page on new search
  };

  const handleSearchCityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTermCity(e.target.value);
    setCurrentPage(1); // Reset to first page on new search
  };

  const handleSortChange = (value: string) => {
    const parts = value.split('-');
    const field = parts[0] || "name"; // Default to "name" if field is missing
    const order = (parts[1] || "asc") as "asc" | "desc";
    
    setSortBy(field);
    setSortOrder(order);
    setCurrentPage(1); // Reset to first page on sort change
  };

  return (
    <div className="space-y-8">
      <header className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Discover Padel Clubs</h1>
        <p className="text-muted-foreground">
          Find the perfect place for your next game.
        </p>
      </header>

      {/* Search and Filters Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 p-4 border rounded-lg items-end">
        <div className="space-y-1">
            <label htmlFor="searchName" className="text-sm font-medium">Search by Name</label>
            <Input 
                id="searchName"
                type="search" 
                placeholder="Club name..." 
                value={searchTermName}
                onChange={handleSearchNameChange}
            />
        </div>
        <div className="space-y-1">
            <label htmlFor="searchCity" className="text-sm font-medium">Filter by City</label>
            <Input 
                id="searchCity"
                type="search" 
                placeholder="City..." 
                value={searchTermCity}
                onChange={handleSearchCityChange}
            />
        </div>
        <div className="space-y-1">
            <label htmlFor="sortBy" className="text-sm font-medium">Sort by</label>
            <Select 
                value={`${sortBy}-${sortOrder}`}
                onValueChange={handleSortChange}
            >
                <SelectTrigger id="sortBy">
                    <SelectValue placeholder="Sort by..." />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="name-asc">Name (A-Z)</SelectItem>
                    <SelectItem value="name-desc">Name (Z-A)</SelectItem>
                    <SelectItem value="city-asc">City (A-Z)</SelectItem>
                    <SelectItem value="city-desc">City (Z-A)</SelectItem>
                </SelectContent>
            </Select>
        </div>
      </div>

      {isLoading && (
        <div className="flex justify-center items-center py-10">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
          <p className="ml-3 text-muted-foreground">Loading clubs...</p>
        </div>
      )}

      {error && (
        <div className="flex flex-col items-center justify-center py-10 bg-destructive/10 p-4 rounded-md">
          <AlertTriangle className="h-10 w-10 text-destructive mb-2" />
          <p className="text-destructive font-semibold">Error loading clubs</p>
          <p className="text-sm text-muted-foreground">{error}</p>
          <Button variant="outline" onClick={fetchClubs} className="mt-4">Try Again</Button>
        </div>
      )}

      {!isLoading && !error && clubs.length === 0 && (
        <div className="text-center py-10">
          <p className="text-xl text-muted-foreground">No clubs found matching your criteria.</p>
        </div>
      )}

      {!isLoading && !error && clubs.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {clubs.map((club) => (
            <Link key={club.id} href={`/clubs/${club.id}`} passHref legacyBehavior>
              <Card className="overflow-hidden hover:shadow-lg transition-shadow duration-200 cursor-pointer h-full flex flex-col">
                <img 
                  src={club.image_url || `https://via.placeholder.com/400x200?text=${encodeURIComponent(club.name)}`}
                  alt={`Image of ${club.name}`}
                  className="w-full h-48 object-cover"
                />
                <CardHeader>
                  <CardTitle className="text-lg truncate" title={club.name}>{club.name}</CardTitle>
                  <CardDescription className="truncate" title={club.city || 'N/A'}>{club.city || 'Location not specified'}</CardDescription>
                </CardHeader>
                <CardContent className="flex-grow">
                  <p className="text-sm text-muted-foreground line-clamp-2" title={club.address || ''}>
                    {club.address || "Address not available"}
                  </p>
                </CardContent>
                <CardFooter>
                    <Button variant="outline" size="sm" className="w-full">View Details</Button>
                </CardFooter>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {!isLoading && !error && (clubs.length > 0 || currentPage > 1) && (
        <div className="flex justify-center items-center space-x-4 mt-8">
          <Button 
            variant="outline" 
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))} 
            disabled={currentPage === 1}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">Page {currentPage}</span>
          <Button 
            variant="outline" 
            onClick={() => setCurrentPage(prev => prev + 1)} 
            disabled={!hasNextPage}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
} 