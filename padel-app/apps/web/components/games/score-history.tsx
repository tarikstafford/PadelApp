"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Badge } from '@workspace/ui/components/badge';
import { Button } from '@workspace/ui/components/button';
import { 
  History, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Clock, 
  User,
  MessageSquare,
  Trophy
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import { format } from 'date-fns';

interface ScoreHistoryProps {
  gameId: number;
  team1Name?: string;
  team2Name?: string;
}

interface GameScore {
  id: number;
  game_id: number;
  team1_score: number;
  team2_score: number;
  submitted_by_team: number;
  submitted_by_user_id: number;
  submitted_at: string;
  status: 'PENDING' | 'CONFIRMED' | 'DISPUTED' | 'RESOLVED';
  final_team1_score?: number;
  final_team2_score?: number;
  confirmed_at?: string;
  admin_resolved: boolean;
  admin_notes?: string;
  submitted_by?: {
    id: number;
    full_name: string;
    email: string;
  };
  confirmations: ScoreConfirmation[];
}

interface ScoreConfirmation {
  id: number;
  game_score_id: number;
  confirming_team: number;
  confirming_user_id: number;
  action: 'CONFIRM' | 'COUNTER';
  confirmed_at: string;
  counter_team1_score?: number;
  counter_team2_score?: number;
  counter_notes?: string;
  confirming_user?: {
    id: number;
    full_name: string;
    email: string;
  };
}

interface ScoreHistoryResponse {
  scores: GameScore[];
  total_count: number;
  latest_score?: GameScore;
}

export function ScoreHistory({ 
  gameId, 
  team1Name = "Team 1", 
  team2Name = "Team 2" 
}: ScoreHistoryProps) {
  const { accessToken } = useAuth();
  const [scoreHistory, setScoreHistory] = useState<ScoreHistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchScoreHistory = async () => {
    if (!accessToken) return;
    
    setIsLoading(true);
    try {
      const response = await apiClient.get<ScoreHistoryResponse>(
        `/games/${gameId}/scores`,
        undefined,
        accessToken
      );
      setScoreHistory(response);
    } catch (error: any) {
      console.error('Error fetching score history:', error);
      // Don't show error toast if user doesn't have permission (expected for non-participants)
      if (error.response?.status !== 403) {
        toast.error('Failed to load score history');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchScoreHistory();
  }, [gameId, accessToken]);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <History className="mr-2 h-5 w-5" />
            Score History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-pulse text-muted-foreground">Loading score history...</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!scoreHistory || scoreHistory.scores.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <History className="mr-2 h-5 w-5" />
            Score History
          </CardTitle>
          <CardDescription>
            No score submissions yet for this game
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'CONFIRMED':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'DISPUTED':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'RESOLVED':
        return <CheckCircle className="h-4 w-4 text-blue-500" />;
      default:
        return <Clock className="h-4 w-4 text-orange-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'CONFIRMED':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'DISPUTED':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'RESOLVED':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-orange-100 text-orange-800 border-orange-200';
    }
  };

  const getWinnerText = (score: GameScore) => {
    const team1Score = score.final_team1_score ?? score.team1_score;
    const team2Score = score.final_team2_score ?? score.team2_score;
    
    if (team1Score > team2Score) {
      return `${team1Name} won ${team1Score}-${team2Score}`;
    } else if (team2Score > team1Score) {
      return `${team2Name} won ${team2Score}-${team1Score}`;
    } else {
      return `Tied ${team1Score}-${team2Score}`;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <History className="mr-2 h-5 w-5" />
          Score History
        </CardTitle>
        <CardDescription>
          {scoreHistory.total_count} score submission{scoreHistory.total_count !== 1 ? 's' : ''} for this game
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {scoreHistory.scores.map((score, index) => (
            <Card key={score.id} className="border-l-4" style={{ borderLeftColor: score.status === 'CONFIRMED' ? '#10b981' : score.status === 'DISPUTED' ? '#ef4444' : '#f59e0b' }}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Badge className={`${getStatusColor(score.status)} flex items-center gap-2`}>
                      {getStatusIcon(score.status)}
                      {score.status}
                    </Badge>
                    <span className="font-medium">
                      {getWinnerText(score)}
                    </span>
                    {index === 0 && (
                      <Badge variant="outline">Latest</Badge>
                    )}
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {format(new Date(score.submitted_at), 'MMM d, HH:mm')}
                  </span>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Score Details */}
                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardContent className="p-4 text-center">
                      <div className="text-2xl font-bold">
                        {score.final_team1_score ?? score.team1_score}
                        {score.final_team1_score && score.final_team1_score !== score.team1_score && (
                          <span className="text-sm text-muted-foreground ml-2">
                            (was {score.team1_score})
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-muted-foreground">{team1Name}</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <div className="text-2xl font-bold">
                        {score.final_team2_score ?? score.team2_score}
                        {score.final_team2_score && score.final_team2_score !== score.team2_score && (
                          <span className="text-sm text-muted-foreground ml-2">
                            (was {score.team2_score})
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-muted-foreground">{team2Name}</div>
                    </CardContent>
                  </Card>
                </div>

                {/* Submission Info */}
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <div className="flex items-center">
                    <User className="h-4 w-4 mr-2" />
                    Submitted by {score.submitted_by?.full_name} 
                    (Team {score.submitted_by_team === 1 ? team1Name : team2Name})
                  </div>
                  <div>
                    {format(new Date(score.submitted_at), 'PPp')}
                  </div>
                </div>

                {/* Confirmations */}
                {score.confirmations.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-medium flex items-center">
                      <MessageSquare className="h-4 w-4 mr-2" />
                      Actions
                    </h4>
                    <div className="space-y-2">
                      {score.confirmations.map((confirmation) => (
                        <div key={confirmation.id} className="border rounded-lg p-3 space-y-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              {confirmation.action === 'CONFIRM' ? (
                                <CheckCircle className="h-4 w-4 text-green-500" />
                              ) : (
                                <XCircle className="h-4 w-4 text-red-500" />
                              )}
                              <span className="font-medium">
                                {confirmation.confirming_user?.full_name} {confirmation.action.toLowerCase()}ed
                              </span>
                            </div>
                            <span className="text-sm text-muted-foreground">
                              {format(new Date(confirmation.confirmed_at), 'PPp')}
                            </span>
                          </div>
                          
                          {confirmation.action === 'COUNTER' && (
                            <div className="mt-2 space-y-1">
                              <div className="text-sm font-medium">
                                Counter proposal: {confirmation.counter_team1_score}-{confirmation.counter_team2_score}
                              </div>
                              {confirmation.counter_notes && (
                                <div className="text-sm text-muted-foreground">
                                  "{confirmation.counter_notes}"
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Admin Resolution */}
                {score.admin_resolved && (
                  <div className="border-l-4 border-blue-500 pl-4 py-2 bg-blue-50 dark:bg-blue-900/10">
                    <div className="flex items-center">
                      <Trophy className="h-4 w-4 mr-2 text-blue-500" />
                      <span className="font-medium">Admin Resolution</span>
                    </div>
                    {score.admin_notes && (
                      <div className="text-sm text-muted-foreground mt-1">
                        {score.admin_notes}
                      </div>
                    )}
                    {score.confirmed_at && (
                      <div className="text-sm text-muted-foreground mt-1">
                        Resolved on {format(new Date(score.confirmed_at), 'PPp')}
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}