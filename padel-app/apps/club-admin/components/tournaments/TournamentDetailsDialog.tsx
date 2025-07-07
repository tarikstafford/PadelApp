'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Calendar, Users, DollarSign, Trophy, Settings } from 'lucide-react';
import { Tournament, TournamentStatus, TournamentType } from '@/lib/types';
import { format } from 'date-fns';
import Link from 'next/link';

interface TournamentDetailsDialogProps {
  tournament: Tournament | null;
  isOpen: boolean;
  onClose: () => void;
}

const statusColors = {
  [TournamentStatus.DRAFT]: 'bg-gray-500',
  [TournamentStatus.REGISTRATION_OPEN]: 'bg-green-500',
  [TournamentStatus.REGISTRATION_CLOSED]: 'bg-yellow-500',
  [TournamentStatus.IN_PROGRESS]: 'bg-blue-500',
  [TournamentStatus.COMPLETED]: 'bg-purple-500',
  [TournamentStatus.CANCELLED]: 'bg-red-500',
};

const statusLabels = {
  [TournamentStatus.DRAFT]: 'Draft',
  [TournamentStatus.REGISTRATION_OPEN]: 'Registration Open',
  [TournamentStatus.REGISTRATION_CLOSED]: 'Registration Closed',
  [TournamentStatus.IN_PROGRESS]: 'In Progress',
  [TournamentStatus.COMPLETED]: 'Completed',
  [TournamentStatus.CANCELLED]: 'Cancelled',
};

const formatTournamentType = (type: TournamentType): string => {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

export default function TournamentDetailsDialog({ 
  tournament, 
  isOpen, 
  onClose 
}: TournamentDetailsDialogProps) {
  if (!tournament) return null;

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'PPP p');
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div>
              <DialogTitle className="text-xl">{tournament.name}</DialogTitle>
              <DialogDescription className="mt-1">
                {formatTournamentType(tournament.tournament_type)}
              </DialogDescription>
            </div>
            <Badge 
              className={`${statusColors[tournament.status]} text-white`}
            >
              {statusLabels[tournament.status]}
            </Badge>
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center text-sm text-muted-foreground">
                <Calendar className="mr-2 h-4 w-4" />
                <span>Start Date</span>
              </div>
              <p className="font-medium">{formatDate(tournament.start_date)}</p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center text-sm text-muted-foreground">
                <Calendar className="mr-2 h-4 w-4" />
                <span>End Date</span>
              </div>
              <p className="font-medium">{formatDate(tournament.end_date)}</p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center text-sm text-muted-foreground">
                <Users className="mr-2 h-4 w-4" />
                <span>Participants</span>
              </div>
              <p className="font-medium">
                {tournament.requires_teams 
                  ? `${tournament.total_registered_teams} / ${tournament.max_participants} teams`
                  : `${tournament.total_registered_participants} / ${tournament.max_participants} players`
                }
              </p>
            </div>
            
            {tournament.entry_fee > 0 && (
              <div className="space-y-2">
                <div className="flex items-center text-sm text-muted-foreground">
                  <DollarSign className="mr-2 h-4 w-4" />
                  <span>Entry Fee</span>
                </div>
                <p className="font-medium">${tournament.entry_fee.toFixed(2)}</p>
              </div>
            )}
          </div>

          {/* Description */}
          {tournament.description && (
            <div>
              <h4 className="font-medium mb-2">Description</h4>
              <p className="text-sm text-muted-foreground">{tournament.description}</p>
            </div>
          )}

          {/* Categories */}
          {tournament.categories && tournament.categories.length > 0 && (
            <div>
              <h4 className="font-medium mb-3">Categories</h4>
              <div className="space-y-3">
                {tournament.categories.map((category) => (
                  <div key={category.id} className="flex justify-between items-center p-3 border rounded-lg">
                    <div>
                      <span className="font-medium">{category.category}</span>
                      <span className="text-sm text-muted-foreground ml-2">
                        (ELO {category.min_elo.toFixed(1)} - {category.max_elo.toFixed(1)})
                      </span>
                    </div>
                    <div className="text-sm">
                      {tournament.requires_teams 
                        ? `${category.current_teams} / ${category.max_participants} teams`
                        : `${category.current_individuals} / ${category.max_participants} players`
                      }
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Registration Deadline */}
          <div className="p-4 bg-muted rounded-lg">
            <div className="flex items-center text-sm text-muted-foreground mb-1">
              <Calendar className="mr-2 h-4 w-4" />
              <span>Registration Deadline</span>
            </div>
            <p className="font-medium">{formatDate(tournament.registration_deadline)}</p>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-4 border-t">
            <Link href={`/tournaments/${tournament.id}`} className="flex-1">
              <Button className="w-full">
                <Trophy className="mr-2 h-4 w-4" />
                View Tournament
              </Button>
            </Link>
            <Link href={`/tournaments/${tournament.id}/manage`}>
              <Button variant="outline">
                <Settings className="mr-2 h-4 w-4" />
                Manage
              </Button>
            </Link>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}