"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';

interface Club {
  id: number;
  name: string;
  address?: string;
  city?: string;
  image_url?: string;
}

interface ClubContextType {
  selectedClub: Club | null;
  availableClubs: Club[];
  isLoading: boolean;
  error: string | null;
  switchClub: (clubId: number) => void;
  isMultiClubMode: boolean;
  refreshClubs: () => void;
}

const ClubContext = createContext<ClubContextType | undefined>(undefined);

export function ClubProvider({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated } = useAuth();
  const [selectedClub, setSelectedClub] = useState<Club | null>(null);
  const [availableClubs, setAvailableClubs] = useState<Club[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchClubs = async () => {
    if (!isAuthenticated) return;

    setIsLoading(true);
    setError(null);

    try {
      // Fetch clubs from both endpoints for comprehensive coverage
      const [myClubResponse, allClubsResponse] = await Promise.allSettled([
        apiClient.get<Club>('/admin/my-club'),
        apiClient.get<Club[]>('/business/my-clubs')
      ]);

      const clubs: Club[] = [];

      // Add primary club if exists
      if (myClubResponse.status === 'fulfilled' && myClubResponse.value) {
        clubs.push(myClubResponse.value);
      }

      // Add additional clubs if exists
      if (allClubsResponse.status === 'fulfilled' && Array.isArray(allClubsResponse.value)) {
        const additionalClubs = allClubsResponse.value.filter(
          (club: Club) => !clubs.some(existingClub => existingClub.id === club.id)
        );
        clubs.push(...additionalClubs);
      }

      setAvailableClubs(clubs);

      // Auto-select the first club if none selected
      if (clubs.length > 0 && !selectedClub) {
        const firstClub = clubs[0];
        if (firstClub) {
          setSelectedClub(firstClub);
          localStorage.setItem('selectedClubId', firstClub.id.toString());
        }
      }
    } catch (err) {
      console.error('Failed to fetch clubs:', err);
      setError('Failed to load clubs. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const switchClub = (clubId: number) => {
    const club = availableClubs.find(c => c.id === clubId);
    if (club) {
      setSelectedClub(club);
      localStorage.setItem('selectedClubId', clubId.toString());
    }
  };

  const refreshClubs = () => {
    fetchClubs();
  };

  // Initialize clubs when user authentication changes
  useEffect(() => {
    if (isAuthenticated && user) {
      fetchClubs();
    } else {
      setAvailableClubs([]);
      setSelectedClub(null);
    }
  }, [isAuthenticated, user]);

  // Restore selected club from localStorage
  useEffect(() => {
    if (availableClubs.length > 0) {
      const savedClubId = localStorage.getItem('selectedClubId');
      if (savedClubId) {
        const club = availableClubs.find(c => c.id === parseInt(savedClubId));
        if (club) {
          setSelectedClub(club);
        }
      }
    }
  }, [availableClubs]);

  const value: ClubContextType = {
    selectedClub,
    availableClubs,
    isLoading,
    error,
    switchClub,
    isMultiClubMode: availableClubs.length > 1,
    refreshClubs,
  };

  return <ClubContext.Provider value={value}>{children}</ClubContext.Provider>;
}

export function useClub() {
  const context = useContext(ClubContext);
  if (context === undefined) {
    throw new Error('useClub must be used within a ClubProvider');
  }
  return context;
}