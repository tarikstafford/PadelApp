"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Button } from '@workspace/ui/components/button';
import { Input } from '@workspace/ui/components/input';
import { Label } from '@workspace/ui/components/label';
import { Alert, AlertDescription } from '@workspace/ui/components/alert';
import { Badge } from '@workspace/ui/components/badge';
import { Separator } from '@workspace/ui/components/separator';
import { Textarea } from '@workspace/ui/components/textarea';
import { 
  Trophy, 
 
  Clock, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Info,
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import { format } from 'date-fns';

interface ScoreSubmissionProps {
  gameId: number;
  team1Name?: string;
  team2Name?: string;
  onScoreSubmitted?: () => void;
}

interface ScoreStatus {
  can_submit: boolean;
  can_confirm: boolean;
  message: string;
  user_team?: number;
  latest_score?: GameScore;
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

export function ScoreSubmission({ 
  gameId, 
  team1Name = "Team 1", 
  team2Name = "Team 2", 
  onScoreSubmitted 
}: ScoreSubmissionProps) {
  const { accessToken } = useAuth();
  const [scoreStatus, setScoreStatus] = useState<ScoreStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Score submission form
  const [team1Score, setTeam1Score] = useState('');
  const [team2Score, setTeam2Score] = useState('');
  
  // Score confirmation/counter form
  const [isCountering, setIsCountering] = useState(false);
  const [counterTeam1Score, setCounterTeam1Score] = useState('');
  const [counterTeam2Score, setCounterTeam2Score] = useState('');
  const [counterNotes, setCounterNotes] = useState('');

  const fetchScoreStatus = useCallback(async () => {
    if (!accessToken) return;
    
    setIsLoading(true);
    try {
      const response = await apiClient.get<ScoreStatus>(
        `/games/${gameId}/scores/status`,
        undefined,
        accessToken
      );
      setScoreStatus(response);
      
      // Pre-fill counter form if there's a disputed score
      if (response.latest_score && response.latest_score.status === 'DISPUTED') {
        setCounterTeam1Score(response.latest_score.team1_score.toString());
        setCounterTeam2Score(response.latest_score.team2_score.toString());
      }
    } catch (error) {
      console.error('Error fetching score status:', error);
      toast.error('Failed to load score status');
    } finally {
      setIsLoading(false);
    }
  }, [gameId, accessToken]);

  const submitScore = async () => {
    if (!accessToken || !scoreStatus) return;
    
    const team1ScoreNum = parseInt(team1Score);
    const team2ScoreNum = parseInt(team2Score);
    
    if (isNaN(team1ScoreNum) || isNaN(team2ScoreNum) || team1ScoreNum < 0 || team2ScoreNum < 0) {
      toast.error('Please enter valid scores (0 or greater)');
      return;
    }
    
    if (team1ScoreNum === team2ScoreNum) {
      toast.error('Games cannot end in a tie. Please enter different scores.');
      return;
    }

    setIsSubmitting(true);
    try {
      await apiClient.post(
        `/games/${gameId}/scores`,
        {
          team1_score: team1ScoreNum,
          team2_score: team2ScoreNum,
          submitted_by_team: scoreStatus.user_team,
        },
        { token: accessToken }
      );
      
      toast.success('Score submitted successfully! Waiting for confirmation from the opposing team.');
      setTeam1Score('');
      setTeam2Score('');
      fetchScoreStatus();
      onScoreSubmitted?.();
    } catch (error: unknown) {
      console.error('Error submitting score:', error);
      const message = (error as any).response?.data?.detail || 'Failed to submit score';
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const confirmScore = async (scoreId: number) => {
    if (!accessToken) return;
    
    setIsSubmitting(true);
    try {
      await apiClient.post(
        `/games/${gameId}/scores/${scoreId}/confirm`,
        { action: 'CONFIRM' },
        { token: accessToken }
      );
      
      toast.success('Score confirmed!');
      fetchScoreStatus();
      onScoreSubmitted?.();
    } catch (error: unknown) {
      console.error('Error confirming score:', error);
      const message = (error as any).response?.data?.detail || 'Failed to confirm score';
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const counterScore = async (scoreId: number) => {
    if (!accessToken) return;
    
    const team1ScoreNum = parseInt(counterTeam1Score);
    const team2ScoreNum = parseInt(counterTeam2Score);
    
    if (isNaN(team1ScoreNum) || isNaN(team2ScoreNum) || team1ScoreNum < 0 || team2ScoreNum < 0) {
      toast.error('Please enter valid scores (0 or greater)');
      return;
    }
    
    if (team1ScoreNum === team2ScoreNum) {
      toast.error('Games cannot end in a tie. Please enter different scores.');
      return;
    }

    setIsSubmitting(true);
    try {
      await apiClient.post(
        `/games/${gameId}/scores/${scoreId}/counter`,
        {
          action: 'COUNTER',
          counter_team1_score: team1ScoreNum,
          counter_team2_score: team2ScoreNum,
          counter_notes: counterNotes,
        },
        { token: accessToken }
      );
      
      toast.success('Score disputed! The original submitting team can now review your counter-proposal.');
      setIsCountering(false);
      setCounterTeam1Score('');
      setCounterTeam2Score('');
      setCounterNotes('');
      fetchScoreStatus();
      onScoreSubmitted?.();
    } catch (error: unknown) {
      console.error('Error countering score:', error);
      const message = (error as any).response?.data?.detail || 'Failed to dispute score';
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    fetchScoreStatus();
  }, [fetchScoreStatus]);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Trophy className="mr-2 h-5 w-5" />
            Game Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-pulse text-muted-foreground">Loading score status...</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!scoreStatus) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Trophy className="mr-2 h-5 w-5" />
            Game Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>Unable to load score information.</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const { latest_score, can_submit, can_confirm, message } = scoreStatus;

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

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Trophy className="mr-2 h-5 w-5" />
          Game Score
        </CardTitle>
        <CardDescription>
          Submit and confirm the final score for this game
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Current Status */}
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>{message}</AlertDescription>
        </Alert>

        {/* Latest Score Display */}
        {latest_score && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Current Score Submission</h3>
              <Badge className={`${getStatusColor(latest_score.status)} flex items-center gap-2`}>
                {getStatusIcon(latest_score.status)}
                {latest_score.status}
              </Badge>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold">{latest_score.final_team1_score ?? latest_score.team1_score}</div>
                  <div className="text-sm text-muted-foreground">{team1Name}</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold">{latest_score.final_team2_score ?? latest_score.team2_score}</div>
                  <div className="text-sm text-muted-foreground">{team2Name}</div>
                </CardContent>
              </Card>
            </div>

            <div className="text-sm text-muted-foreground">
              Submitted by {latest_score.submitted_by?.full_name} on{' '}
              {format(new Date(latest_score.submitted_at), 'PPp')}
              {latest_score.confirmed_at && (
                <span>
                  {' '}• Confirmed on {format(new Date(latest_score.confirmed_at), 'PPp')}
                </span>
              )}
            </div>

            {/* Show confirmations */}
            {latest_score.confirmations.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium">Confirmations:</h4>
                {latest_score.confirmations.map((confirmation) => (
                  <div key={confirmation.id} className="flex items-center justify-between text-sm">
                    <span>
                      {confirmation.confirming_user?.full_name} ({confirmation.action.toLowerCase()})
                    </span>
                    <span className="text-muted-foreground">
                      {format(new Date(confirmation.confirmed_at), 'PPp')}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Score Submission Form */}
        {can_submit && (
          <div className="space-y-4">
            <Separator />
            <h3 className="font-semibold">Submit Score</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="team1-score">{team1Name} Score</Label>
                <Input
                  id="team1-score"
                  type="number"
                  min="0"
                  value={team1Score}
                  onChange={(e) => setTeam1Score(e.target.value)}
                  placeholder="0"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="team2-score">{team2Name} Score</Label>
                <Input
                  id="team2-score"
                  type="number"
                  min="0"
                  value={team2Score}
                  onChange={(e) => setTeam2Score(e.target.value)}
                  placeholder="0"
                />
              </div>
            </div>
            <Button 
              onClick={submitScore} 
              disabled={isSubmitting || !team1Score || !team2Score}
              className="w-full"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Score'}
            </Button>
          </div>
        )}

        {/* Score Confirmation */}
        {can_confirm && latest_score && (
          <div className="space-y-4">
            <Separator />
            <h3 className="font-semibold">Confirm or Dispute Score</h3>
            
            {!isCountering ? (
              <div className="flex gap-2">
                <Button 
                  onClick={() => confirmScore(latest_score.id)} 
                  disabled={isSubmitting}
                  className="flex-1"
                >
                  <CheckCircle className="mr-2 h-4 w-4" />
                  {isSubmitting ? 'Confirming...' : 'Confirm Score'}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setIsCountering(true)}
                  className="flex-1"
                >
                  <XCircle className="mr-2 h-4 w-4" />
                  Dispute Score
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="counter-team1-score">{team1Name} Score</Label>
                    <Input
                      id="counter-team1-score"
                      type="number"
                      min="0"
                      value={counterTeam1Score}
                      onChange={(e) => setCounterTeam1Score(e.target.value)}
                      placeholder="0"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="counter-team2-score">{team2Name} Score</Label>
                    <Input
                      id="counter-team2-score"
                      type="number"
                      min="0"
                      value={counterTeam2Score}
                      onChange={(e) => setCounterTeam2Score(e.target.value)}
                      placeholder="0"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="counter-notes">Reason for Dispute (Optional)</Label>
                  <Textarea
                    id="counter-notes"
                    value={counterNotes}
                    onChange={(e) => setCounterNotes(e.target.value)}
                    placeholder="Explain why you disagree with the submitted score..."
                    rows={3}
                  />
                </div>
                <div className="flex gap-2">
                  <Button 
                    onClick={() => counterScore(latest_score.id)} 
                    disabled={isSubmitting || !counterTeam1Score || !counterTeam2Score}
                    className="flex-1"
                  >
                    {isSubmitting ? 'Submitting...' : 'Submit Counter Score'}
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setIsCountering(false);
                      setCounterTeam1Score('');
                      setCounterTeam2Score('');
                      setCounterNotes('');
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}