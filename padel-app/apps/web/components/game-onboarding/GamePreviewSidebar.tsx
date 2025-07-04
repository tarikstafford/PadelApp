"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Badge } from '@workspace/ui/components/badge';
import { Button } from '@workspace/ui/components/button';
import { useGameOnboarding } from './GameOnboardingProvider';
import { useAuth } from '@/contexts/AuthContext';
import { MapPin, Clock, Users, Trophy, User } from 'lucide-react';
import { format } from 'date-fns';

interface GamePreviewSidebarProps {
  className?: string;
}

export function GamePreviewSidebar({ className = '' }: GamePreviewSidebarProps) {
  const { gameData, currentStep, setCurrentStep, joinGame, isLoading } = useGameOnboarding();
  const { user } = useAuth();

  if (!gameData) {
    return (
      <Card className={`w-full ${className}`}>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const { game, creator, is_full, is_expired, can_join } = gameData;
  const { booking } = game;
  const { court } = booking;

  const formatDateTime = (dateTime: string) => {
    return format(new Date(dateTime), 'EEE, MMM d • h:mm a');
  };

  const getGameStatusBadge = () => {
    if (is_expired) return <Badge variant="destructive">Expired</Badge>;
    if (is_full) return <Badge variant="secondary">Full</Badge>;
    if (game.game_status === 'CANCELLED') return <Badge variant="destructive">Cancelled</Badge>;
    return <Badge variant="default">Open</Badge>;
  };

  const getCurrentPlayers = () => {
    return game.players?.filter(p => p.status === 'ACCEPTED') || [];
  };

  const getAvailableSlots = () => {
    const currentPlayers = getCurrentPlayers();
    return 4 - currentPlayers.length;
  };

  const handleJoinClick = () => {
    if (!user) {
      setCurrentStep('auth');
    } else if (can_join && !is_full && !is_expired) {
      joinGame();
    }
  };

  const isUserInGame = user && getCurrentPlayers().some(p => p.user.id === user.id);

  return (
    <Card className={`w-full ${className} sticky top-4`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">Game Invitation</CardTitle>
          {getGameStatusBadge()}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Game Details */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <MapPin className="h-4 w-4" />
            <div>
              <p className="font-medium text-foreground">{court.name}</p>
              <p>{court.club?.name}</p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-sm">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span>{formatDateTime(booking.start_time)}</span>
          </div>

          <div className="flex items-center gap-2 text-sm">
            <Users className="h-4 w-4 text-muted-foreground" />
            <span>{getCurrentPlayers().length}/4 players</span>
            {getAvailableSlots() > 0 && (
              <span className="text-muted-foreground">
                • {getAvailableSlots()} spot{getAvailableSlots() > 1 ? 's' : ''} available
              </span>
            )}
          </div>

          {game.skill_level && (
            <div className="flex items-center gap-2 text-sm">
              <Trophy className="h-4 w-4 text-muted-foreground" />
              <span>Skill Level: {game.skill_level}</span>
            </div>
          )}
        </div>

        {/* Game Creator */}
        <div className="border-t pt-3">
          <div className="flex items-center gap-2 text-sm">
            <User className="h-4 w-4 text-muted-foreground" />
            <span>Created by <span className="font-medium">{creator.full_name || creator.email}</span></span>
          </div>
        </div>

        {/* Current Players */}
        {getCurrentPlayers().length > 0 && (
          <div className="border-t pt-3">
            <h4 className="text-sm font-medium mb-2">Current Players</h4>
            <div className="space-y-1">
              {getCurrentPlayers().map((player) => (
                <div key={player.user.id} className="flex items-center justify-between text-sm">
                  <span>{player.user.full_name || player.user.email}</span>
                  <Badge variant="outline" className="text-xs">
                    ELO {player.elo_rating}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="border-t pt-4">
          {isUserInGame ? (
            <Badge variant="default" className="w-full justify-center py-2">
              You're in this game!
            </Badge>
          ) : currentStep === 'success' ? (
            <Badge variant="default" className="w-full justify-center py-2">
              Successfully joined!
            </Badge>
          ) : (
            <Button
              onClick={handleJoinClick}
              disabled={!can_join || is_full || is_expired || isLoading || currentStep === 'joining'}
              className="w-full"
              size="lg"
            >
              {isLoading || currentStep === 'joining' ? (
                'Joining...'
              ) : !user ? (
                'Sign In to Join'
              ) : !can_join ? (
                'Cannot Join'
              ) : is_full ? (
                'Game Full'
              ) : is_expired ? (
                'Invitation Expired'
              ) : (
                'Join Game'
              )}
            </Button>
          )}

          {/* Game Type Badge */}
          <div className="flex justify-center mt-2">
            <Badge variant="outline" className="text-xs">
              {game.game_type.charAt(0) + game.game_type.slice(1).toLowerCase()} Game
            </Badge>
          </div>
        </div>

        {/* Error Display */}
        {(is_expired || is_full || !can_join) && (
          <div className="text-xs text-muted-foreground text-center">
            {is_expired && "This invitation has expired."}
            {is_full && !is_expired && "This game is full."}
            {!can_join && !is_full && !is_expired && "Unable to join this game."}
          </div>
        )}
      </CardContent>
    </Card>
  );
}