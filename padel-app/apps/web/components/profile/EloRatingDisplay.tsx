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
import { EloRatingWithBadge, ELO_CATEGORIES } from "@/components/shared/EloBadge";

interface EloRatingDisplayProps {
  eloRating: number;
}

export const EloRatingDisplay = ({ eloRating }: EloRatingDisplayProps) => {
  const [showEloInfo, setShowEloInfo] = useState(false);

  return (
    <>
      <div className="flex items-center space-x-2">
        <EloRatingWithBadge eloRating={eloRating} size="md" />
        <Button variant="ghost" size="sm" onClick={() => setShowEloInfo(true)}>
          <InfoIcon className="h-4 w-4" />
        </Button>
      </div>

      <Dialog open={showEloInfo} onOpenChange={setShowEloInfo}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Padel ELO Rating Categories</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {ELO_CATEGORIES.map((category) => (
              <div key={category.name} className="flex items-center gap-3">
                <div className={`w-12 h-12 ${category.bgColor} ${category.borderColor} border-2 rounded-lg flex items-center justify-center`}>
                  <span className="text-xl">{category.icon}</span>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{category.name}</span>
                    <span className="text-sm text-muted-foreground">({category.range})</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {category.name === 'Bronze' && 'Beginners learning fundamentals and basic techniques'}
                    {category.name === 'Silver' && 'Developing consistency, positioning, and game awareness'}
                    {category.name === 'Gold' && 'Advanced tactical play, strong shots, and strategy'}
                    {category.name === 'Platinum' && 'Elite players with professional-level skills'}
                  </p>
                </div>
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button onClick={() => setShowEloInfo(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}; 