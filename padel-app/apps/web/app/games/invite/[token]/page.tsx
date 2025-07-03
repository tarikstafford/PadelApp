'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar, Clock, MapPin, Users, Loader2, AlertTriangle } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import { toast } from 'sonner';
import Link from 'next/link';

interface GameInvitationInfo {
  game_id: number;
  game_name: string;
  creator_name: string;
  start_time: string;
  end_time: string;
  court_name: string;
  club_name: string;
  current_players: number;
  max_players: number;
  is_valid: boolean;
  expires_at: string;
}

export default function GameInvitePage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const isAuthenticated = !!user;
  const [invitationInfo, setInvitationInfo] = useState<GameInvitationInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const token = params.token as string;

  const fetchInvitationInfo = useCallback(async () => {
    try {
      setLoading(true);
      const response = await apiClient.get<GameInvitationInfo>(
        `/games/invitations/${token}/info`,
        {},
        null,
        false // Don't require auth for this call
      );
      setInvitationInfo(response);
    } catch (error: any) {
      console.error('Failed to fetch invitation info:', error);
      setError('Invalid or expired invitation link');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (token) {
      fetchInvitationInfo();
    }
  }, [token, fetchInvitationInfo]);

  const handleJoinGame = async () => {
    if (!isAuthenticated) {
      // Store the current URL to redirect back after auth
      sessionStorage.setItem('redirectAfterAuth', window.location.href);
      router.push('/auth/login');
      return;
    }

    try {
      setJoining(true);
      const response = await apiClient.post(
        `/games/invitations/${token}/accept`,
        {}
      ) as { message?: string; game_id?: number };
      
      toast.success(response.message || 'Successfully joined the game!');
      router.push(`/games/${invitationInfo?.game_id}`);
    } catch (error: any) {
      console.error('Failed to join game:', error);
      toast.error(error.response?.data?.detail || 'Failed to join game');
    } finally {
      setJoining(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-md mx-4">
          <CardContent className="pt-6">
            <div className="flex items-center justify-center space-x-2">
              <Loader2 className="h-6 w-6 animate-spin" />
              <span>Loading invitation...</span>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !invitationInfo) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-md mx-4">
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <AlertTriangle className="h-12 w-12 text-red-500 mx-auto" />
              <div>
                <h3 className="text-lg font-semibold">Invalid Invitation</h3>
                <p className="text-muted-foreground">{error}</p>
              </div>
              <Button asChild>
                <Link href="/games">Browse Games</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!invitationInfo.is_valid) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-md mx-4">
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto" />
              <div>
                <h3 className="text-lg font-semibold">Invitation Expired</h3>
                <p className="text-muted-foreground">
                  This invitation link has expired or is no longer valid.
                </p>
              </div>
              <Button asChild>
                <Link href="/games">Browse Games</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isFull = invitationInfo.current_players >= invitationInfo.max_players;

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">Game Invitation</CardTitle>
              <CardDescription>
                {invitationInfo.creator_name} has invited you to join a padel game
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Game Details */}
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <MapPin className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">{invitationInfo.court_name}</p>
                    <p className="text-sm text-muted-foreground">{invitationInfo.club_name}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <Calendar className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">
                      {format(parseISO(invitationInfo.start_time), 'EEEE, MMMM d, yyyy')}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <Clock className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">
                      {format(parseISO(invitationInfo.start_time), 'h:mm a')} - {format(parseISO(invitationInfo.end_time), 'h:mm a')}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <Users className="h-5 w-5 text-muted-foreground" />
                  <div className="flex items-center space-x-2">
                    <p className="font-medium">
                      {invitationInfo.current_players}/{invitationInfo.max_players} players
                    </p>
                    {isFull ? (
                      <Badge variant="destructive">Full</Badge>
                    ) : (
                      <Badge variant="secondary">
                        {invitationInfo.max_players - invitationInfo.current_players} spots left
                      </Badge>
                    )}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-4 space-y-3">
                {isFull ? (
                  <div className="text-center">
                    <p className="text-muted-foreground mb-4">This game is already full</p>
                    <Button asChild variant="outline">
                      <Link href="/games">Browse Other Games</Link>
                    </Button>
                  </div>
                ) : !isAuthenticated ? (
                  <div className="space-y-3">
                    <p className="text-center text-muted-foreground">
                      Sign in to join this game
                    </p>
                    <div className="flex flex-col space-y-2">
                      <Button onClick={handleJoinGame} className="w-full">
                        Sign In & Join Game
                      </Button>
                      <Button asChild variant="outline" className="w-full">
                        <Link href="/auth/register">Create Account & Join</Link>
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <Button 
                      onClick={handleJoinGame} 
                      disabled={joining}
                      className="w-full"
                    >
                      {joining ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Joining...
                        </>
                      ) : (
                        'Join Game'
                      )}
                    </Button>
                    <p className="text-center text-sm text-muted-foreground">
                      Signed in as {user?.full_name || user?.email}
                    </p>
                  </div>
                )}
              </div>

              {/* Invitation Expiry */}
              <div className="pt-4 border-t">
                <p className="text-xs text-muted-foreground text-center">
                  This invitation expires on {format(parseISO(invitationInfo.expires_at), 'PPpp')}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}