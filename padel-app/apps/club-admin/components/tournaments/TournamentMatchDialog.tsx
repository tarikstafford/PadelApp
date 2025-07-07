'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Calendar, Users, MapPin, Trophy, Settings } from 'lucide-react';
import { TournamentMatch, MatchStatus } from '@/lib/types';
import { format } from 'date-fns';

interface TournamentMatchDialogProps {
  match: TournamentMatch | null;
  isOpen: boolean;
  onClose: () => void;
}

const statusColors = {
  [MatchStatus.PENDING]: 'bg-yellow-500',
  [MatchStatus.IN_PROGRESS]: 'bg-blue-500',
  [MatchStatus.COMPLETED]: 'bg-green-500',
  [MatchStatus.CANCELLED]: 'bg-red-500',
  [MatchStatus.POSTPONED]: 'bg-gray-500',
};

const statusLabels = {
  [MatchStatus.PENDING]: 'Pending',
  [MatchStatus.IN_PROGRESS]: 'In Progress',
  [MatchStatus.COMPLETED]: 'Completed',
  [MatchStatus.CANCELLED]: 'Cancelled',
  [MatchStatus.POSTPONED]: 'Postponed',
};

export default function TournamentMatchDialog({ 
  match, 
  isOpen, 
  onClose 
}: TournamentMatchDialogProps) {
  if (!match) return null;

  const formatDateTime = (dateString: string) => {
    return format(new Date(dateString), 'PPP p');
  };

  const getScoreDisplay = () => {
    if (match.status === MatchStatus.COMPLETED && match.team1_score !== undefined && match.team2_score !== undefined) {
      return `${match.team1_score} - ${match.team2_score}`;
    }
    return null;
  };

  const getWinnerDisplay = () => {
    if (match.status === MatchStatus.COMPLETED && match.winning_team_id) {
      if (match.winning_team_id === match.team1_id) {
        return match.team1_name || 'Team 1';
      } else if (match.winning_team_id === match.team2_id) {
        return match.team2_name || 'Team 2';
      }
    }
    return null;
  };

  const score = getScoreDisplay();
  const winner = getWinnerDisplay();

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div>
              <DialogTitle className="text-lg">
                Tournament Match - Round {match.round_number}
              </DialogTitle>
              <DialogDescription className="mt-1">
                Match #{match.match_number} • {match.category} Category
              </DialogDescription>
            </div>
            <Badge 
              className={`${statusColors[match.status]} text-white`}
            >
              {statusLabels[match.status]}
            </Badge>
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Teams */}
          <div className="text-center">
            <div className="flex items-center justify-center space-x-4">
              <div className="text-center">
                <div className="font-semibold text-lg">
                  {match.team1_name || 'TBD'}
                </div>
                {score && (
                  <div className="text-2xl font-bold text-primary">
                    {match.team1_score}
                  </div>
                )}
              </div>
              
              <div className="text-muted-foreground font-medium">
                VS
              </div>
              
              <div className="text-center">
                <div className="font-semibold text-lg">
                  {match.team2_name || 'TBD'}
                </div>
                {score && (
                  <div className="text-2xl font-bold text-primary">
                    {match.team2_score}
                  </div>
                )}
              </div>
            </div>
            
            {winner && (
              <div className="mt-3 p-2 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center justify-center text-green-700">
                  <Trophy className="mr-2 h-4 w-4" />
                  <span className="font-medium">Winner: {winner}</span>
                </div>
              </div>
            )}
          </div>

          {/* Match Details */}
          <div className="space-y-4">
            {match.scheduled_time && (
              <div className="flex items-center">
                <Calendar className="mr-3 h-4 w-4 text-muted-foreground" />
                <div>
                  <div className="font-medium">Scheduled Time</div>
                  <div className="text-sm text-muted-foreground">
                    {formatDateTime(match.scheduled_time)}
                  </div>
                </div>
              </div>
            )}

            {match.court_name && (
              <div className="flex items-center">
                <MapPin className="mr-3 h-4 w-4 text-muted-foreground" />
                <div>
                  <div className="font-medium">Court</div>
                  <div className="text-sm text-muted-foreground">
                    {match.court_name}
                  </div>
                </div>
              </div>
            )}

            <div className="flex items-center">
              <Users className="mr-3 h-4 w-4 text-muted-foreground" />
              <div>
                <div className="font-medium">Category</div>
                <div className="text-sm text-muted-foreground">
                  {match.category}
                </div>
              </div>
            </div>
          </div>

          {/* Match Status Info */}
          {match.status === MatchStatus.PENDING && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-700">
                This match is waiting to be played. Check back for updates.
              </p>
            </div>
          )}

          {match.status === MatchStatus.IN_PROGRESS && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-700">
                This match is currently in progress.
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 pt-4 border-t">
            <Button 
              variant="outline" 
              onClick={onClose}
              className="flex-1"
            >
              Close
            </Button>
            {(match.status === MatchStatus.PENDING || match.status === MatchStatus.IN_PROGRESS) && (
              <Button className="flex-1">
                <Settings className="mr-2 h-4 w-4" />
                Manage Match
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}