"use client";

import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@workspace/ui/components/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
} from "@workspace/ui/components/dialog";
import { Input } from "@workspace/ui/components/input";
import { Label } from "@workspace/ui/components/label";
import { Textarea } from "@workspace/ui/components/textarea";
import { toast } from "sonner";

interface EloAdjustmentRequestModalProps {
  canMakeRequest: boolean;
}

export const EloAdjustmentRequestModal = ({ canMakeRequest }: EloAdjustmentRequestModalProps) => {
  const { requestEloAdjustment } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [requestedRating, setRequestedRating] = useState("");
  const [reason, setReason] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await requestEloAdjustment(parseFloat(requestedRating), reason);
      toast.success("Your ELO adjustment request has been submitted.");
      setIsOpen(false);
    } catch {
      toast.error("Failed to submit your request. Please try again.");
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button disabled={!canMakeRequest}>Request Rating Adjustment</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Request ELO Adjustment</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="rating" className="text-right">
                Requested Rating
              </Label>
              <Input
                id="rating"
                type="number"
                value={requestedRating}
                onChange={(e) => setRequestedRating(e.target.value)}
                className="col-span-3"
                step="0.1"
                min="1.0"
                max="7.0"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="reason" className="text-right">
                Reason
              </Label>
              <Textarea
                id="reason"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="col-span-3"
                minLength={10}
                maxLength={500}
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="submit">Submit Request</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}; 