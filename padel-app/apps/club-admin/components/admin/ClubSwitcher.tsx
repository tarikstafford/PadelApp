"use client";

import { useState } from 'react';
import { ChevronDown, Building2, Check } from 'lucide-react';
import { useClub } from '@/contexts/ClubContext';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

export function ClubSwitcher() {
  const { selectedClub, availableClubs, isMultiClubMode, switchClub, isLoading } = useClub();
  const [isOpen, setIsOpen] = useState(false);

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="h-8 w-8 rounded-full bg-gray-200 animate-pulse" />
        <div className="h-4 w-32 bg-gray-200 animate-pulse rounded" />
      </div>
    );
  }

  if (!selectedClub) {
    return (
      <div className="flex items-center space-x-2 text-gray-500">
        <Building2 className="h-5 w-5" />
        <span className="text-sm">No club selected</span>
      </div>
    );
  }

  // Single club mode - just show the club name
  if (!isMultiClubMode) {
    return (
      <div className="flex items-center space-x-2">
        <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
          <Building2 className="h-4 w-4 text-blue-600" />
        </div>
        <div>
          <div className="text-sm font-medium">{selectedClub.name}</div>
          {selectedClub.city && (
            <div className="text-xs text-gray-500">{selectedClub.city}</div>
          )}
        </div>
      </div>
    );
  }

  // Multi-club mode - show dropdown
  return (
    <div className="relative">
      <Button
        variant="outline"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 h-auto p-2 justify-between min-w-48"
      >
        <div className="flex items-center space-x-2">
          <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
            <Building2 className="h-4 w-4 text-blue-600" />
          </div>
          <div className="text-left">
            <div className="text-sm font-medium">{selectedClub.name}</div>
            {selectedClub.city && (
              <div className="text-xs text-gray-500">{selectedClub.city}</div>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-1">
          <Badge variant="secondary" className="text-xs">
            {availableClubs.length}
          </Badge>
          <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </div>
      </Button>

      {isOpen && (
        <Card className="absolute top-full left-0 mt-1 min-w-full z-50 shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Switch Club</CardTitle>
            <CardDescription className="text-xs">
              Select a club to manage
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="max-h-64 overflow-y-auto">
              {availableClubs.map((club) => (
                <button
                  key={club.id}
                  onClick={() => {
                    switchClub(club.id);
                    setIsOpen(false);
                  }}
                  className="w-full text-left p-3 hover:bg-gray-50 flex items-center justify-between group"
                >
                  <div className="flex items-center space-x-2">
                    <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                      <Building2 className="h-4 w-4 text-blue-600" />
                    </div>
                    <div>
                      <div className="text-sm font-medium">{club.name}</div>
                      {club.city && (
                        <div className="text-xs text-gray-500">{club.city}</div>
                      )}
                    </div>
                  </div>
                  {selectedClub.id === club.id && (
                    <Check className="h-4 w-4 text-blue-600" />
                  )}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Overlay to close dropdown when clicking outside */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}