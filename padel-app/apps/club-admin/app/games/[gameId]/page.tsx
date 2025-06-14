"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { apiClient } from "@/lib/api";
import { Game } from "@/lib/types";
import { Avatar, AvatarFallback, AvatarImage } from "@workspace/ui/components/avatar";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@workspace/ui/components/tooltip";
import { Button } from "@workspace/ui/components/button";
import { toast } from "sonner";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@workspace/ui/components/alert-dialog"

export default function GameDetailPage() {
  const { user } = useAuth();
  const params = useParams();
  const gameId = params.gameId as string;
  const [game, setGame] = useState<Game | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const fetchGameDetails = () => {
    if (user && gameId) {
      setLoading(true);
      apiClient.get<Game>(`/games/${gameId}`)
        .then(data => {
          setGame(data);
        })
        .catch(error => {
          console.error("Failed to fetch game details", error);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }

  useEffect(() => {
    fetchGameDetails();
  }, [user, gameId]);

  const handleSubmitResult = async (winningTeamId: number) => {
    setSubmitting(true);
    try {
      await apiClient.post(`/games/${gameId}/result`, { winning_team_id: winningTeamId });
      toast.success("Game result submitted successfully!");
      fetchGameDetails();
    } catch (error) {
      console.error("Failed to submit game result", error);
      toast.error("Failed to submit game result. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <div>Loading game details...</div>;
  }

  if (!game) {
    return <div>Game not found.</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Game Details</h1>
      <div className="flex justify-around">
        <div>
          <h2 className="text-xl font-bold mb-2">Team 1</h2>
          {game.team1?.players.map(player => (
            <div key={player.id} className="flex items-center space-x-2 mb-2">
              <Avatar>
                <AvatarImage src={player.user.profile_picture_url || undefined} />
                <AvatarFallback>{player.user.full_name?.substring(0, 2)}</AvatarFallback>
              </Avatar>
              <div>
                <p>{player.user.full_name}</p>
                <p className="text-sm text-gray-500">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger>ELO: {player.user.elo_rating.toFixed(1)}</TooltipTrigger>
                      <TooltipContent>
                        <p>Padel Skill Levels</p>
                        <p><strong>Level 1:</strong> Beginner</p>
                        <p><strong>Level 2:</strong> Lower intermediate</p>
                        <p><strong>Level 3–4:</strong> Intermediate</p>
                        <p><strong>Level 4–5:</strong> Advanced</p>
                        <p><strong>Level 6–7:</strong> Professional</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </p>
              </div>
            </div>
          ))}
        </div>
        <div>
          <h2 className="text-xl font-bold mb-2">Team 2</h2>
          {game.team2?.players.map(player => (
            <div key={player.id} className="flex items-center space-x-2 mb-2">
              <Avatar>
                <AvatarImage src={player.user.profile_picture_url || undefined} />
                <AvatarFallback>{player.user.full_name?.substring(0, 2)}</AvatarFallback>
              </Avatar>
              <div>
                <p>{player.user.full_name}</p>
                <p className="text-sm text-gray-500">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger>ELO: {player.user.elo_rating.toFixed(1)}</TooltipTrigger>
                      <TooltipContent>
                        <p>Padel Skill Levels</p>
                        <p><strong>Level 1:</strong> Beginner</p>
                        <p><strong>Level 2:</strong> Lower intermediate</p>
                        <p><strong>Level 3–4:</strong> Intermediate</p>
                        <p><strong>Level 4–5:</strong> Advanced</p>
                        <p><strong>Level 6–7:</strong> Professional</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {!game.result_submitted && (
        <div className="mt-8">
          <h2 className="text-xl font-bold mb-4">Submit Result</h2>
          <div className="flex space-x-4">
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button disabled={submitting}>Team 1 Won</Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This action cannot be undone. This will permanently submit the game result and update player ELO ratings.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={() => handleSubmitResult(game.team1!.id)}>Continue</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button disabled={submitting}>Team 2 Won</Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This action cannot be undone. This will permanently submit the game result and update player ELO ratings.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={() => handleSubmitResult(game.team2!.id)}>Continue</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>
      )}

      {game.result_submitted && (
        <div className="mt-8">
          <h2 className="text-xl font-bold mb-4">Result Submitted</h2>
          <p>Winning Team: {game.winning_team_id === game.team1?.id ? 'Team 1' : 'Team 2'}</p>
        </div>
      )}
    </div>
  );
} 