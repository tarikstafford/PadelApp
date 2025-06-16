"use client";

import { useState } from "react";
import { Button } from "@workspace/ui/components/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@workspace/ui/components/dialog";
import { InfoIcon } from "lucide-react";

interface EloRatingDisplayProps {
  eloRating: number;
}

export const EloRatingDisplay = ({ eloRating }: EloRatingDisplayProps) => {
  const [showEloInfo, setShowEloInfo] = useState(false);

  return (
    <>
      <div className="flex items-center space-x-2">
        <span className="text-lg font-semibold">{eloRating.toFixed(1)}</span>
        <Button variant="ghost" size="sm" onClick={() => setShowEloInfo(true)}>
          <InfoIcon className="h-4 w-4" />
        </Button>
      </div>

      <Dialog open={showEloInfo} onOpenChange={setShowEloInfo}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Padel Skill Levels</DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            <p>
              <strong>Level 1:</strong> Beginner – just learning fundamentals.
            </p>
            <p>
              <strong>Level 2:</strong> Lower intermediate – developing
              consistency and positioning.
            </p>
            <p>
              <strong>Level 3–4:</strong> Intermediate – tactical play and
              stronger shots.
            </p>
            <p>
              <strong>Level 4–5:</strong> Advanced – high control, strategy,
              experience.
            </p>
            <p>
              <strong>Level 6–7:</strong> Professional – national/international
              competitor.
            </p>
          </div>
          <DialogFooter>
            <Button onClick={() => setShowEloInfo(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}; 