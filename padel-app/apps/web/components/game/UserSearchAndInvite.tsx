"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@workspace/ui/components/button';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@workspace/ui/components/command';
import { Loader2, UserPlus } from 'lucide-react';
import { toast } from 'sonner';

// Export the interface to be used by other components
export interface UserSearchResult {
  id: number;
  name?: string | null;
  email: string;
}

interface GamePlayer {
    user: UserSearchResult;
    status: string; // e.g., "ACCEPTED", "INVITED", "DECLINED"
}

interface UserSearchAndInviteProps {
  gameId: number;
  currentPlayers: GamePlayer[]; // To avoid inviting already present players
  onPlayerInvited: (invitedPlayer: UserSearchResult) => void; // Callback after successful invitation
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// A more correctly typed debounce function
function debounce<T extends (...args: any[]) => void>(func: T, delay: number) {
  let timeoutId: NodeJS.Timeout | undefined;
  return function(this: ThisParameterType<T>, ...args: Parameters<T>) {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      func.apply(this, args);
    }, delay);
  };
}

export default function UserSearchAndInvite({ gameId, currentPlayers, onPlayerInvited }: UserSearchAndInviteProps) {
  const { accessToken } = useAuth();
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState<UserSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [inviteLoading, setInviteLoading] = useState<Record<number, boolean>>({}); // { userId: isLoading }

  // Debounce search function
  const debouncedSearch = useCallback(
    debounce(async (query: string) => {
      if (!query.trim() || query.trim().length < 2) { // Minimum 2 chars to search
        setSearchResults([]);
        setIsSearching(false);
        return;
      }
      setIsSearching(true);
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/users/search?query=${encodeURIComponent(query)}&limit=5`, {
          headers: { 'Authorization': `Bearer ${accessToken}` },
        });
        if (!response.ok) {
          throw new Error("Failed to search users");
        }
        const data: UserSearchResult[] = await response.json();
        // Filter out users already in the game from search results
        const currentPlayerIds = new Set(currentPlayers.map(p => p.user.id));
        setSearchResults(data.filter(u => !currentPlayerIds.has(u.id)));
      } catch (error) {
        console.error("User search error:", error);
        toast.error("Failed to search users.");
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 500), // 500ms debounce delay
    [accessToken, currentPlayers] // Dependencies for useCallback
  );

  useEffect(() => {
    debouncedSearch(searchTerm);
  }, [searchTerm, debouncedSearch]);

  const handleInvite = async (userToInvite: UserSearchResult) => {
    if (!accessToken) {
      toast.error("Not authenticated.");
      return;
    }
    setInviteLoading(prev => ({ ...prev, [userToInvite.id]: true }));
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/games/${gameId}/invitations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ user_id_to_invite: userToInvite.id }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to send invitation.");
      }
      toast.success(`Invitation sent to ${userToInvite.name || userToInvite.email}`);
      onPlayerInvited(userToInvite); // Notify parent to refresh player list
      setSearchTerm(""); // Clear search term after inviting
      setSearchResults([]); // Clear results
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Failed to send invitation.";
      console.error("Invite error:", error);
      toast.error(message);
    } finally {
      setInviteLoading(prev => ({ ...prev, [userToInvite.id]: false }));
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium">Invite Players</h3>
      <Command className="rounded-lg border shadow-sm">
        <CommandInput 
            placeholder="Search for users by name or email..." 
            value={searchTerm}
            onValueChange={setSearchTerm} // Use onValueChange for CommandInput
        />
        <CommandList>
          {isSearching && <CommandItem className="justify-center"><Loader2 className="mr-2 h-4 w-4 animate-spin" />Searching...</CommandItem>}
          {!isSearching && searchTerm.trim().length > 1 && searchResults.length === 0 && (
            <CommandEmpty>No users found.</CommandEmpty>
          )}
          {!isSearching && searchResults.length > 0 && (
            <CommandGroup heading="Search Results">
              {searchResults.map((userRes) => (
                <CommandItem 
                  key={userRes.id} 
                  className="flex justify-between items-center"
                >
                  <div>
                    <p className="text-sm font-medium">{userRes.name || 'N/A'}</p>
                    <p className="text-xs text-muted-foreground">{userRes.email}</p>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleInvite(userRes)}
                    disabled={inviteLoading[userRes.id]}
                  >
                    {inviteLoading[userRes.id] ? <Loader2 className="h-4 w-4 animate-spin" /> : <UserPlus className="mr-1 h-4 w-4" />} 
                    Invite
                  </Button>
                </CommandItem>
              ))}
            </CommandGroup>
          )}
        </CommandList>
      </Command>
    </div>
  );
} 