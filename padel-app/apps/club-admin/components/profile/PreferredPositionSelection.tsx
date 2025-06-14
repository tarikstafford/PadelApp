"use client";

import { useAuth } from "@/contexts/AuthContext";
import { Label } from "@workspace/ui/components/label";
import { RadioGroup, RadioGroupItem } from "@workspace/ui/components/radio-group";

export const PreferredPositionSelection = () => {
  const { user, updatePreferredPosition } = useAuth();

  return (
    <RadioGroup
      value={user?.preferred_position || ""}
      onValueChange={(val) =>
        updatePreferredPosition(val as "LEFT" | "RIGHT")
      }
      className="flex space-x-4"
    >
      <div className="flex items-center space-x-2">
        <RadioGroupItem value="LEFT" id="left" />
        <Label htmlFor="left">Left</Label>
      </div>
      <div className="flex items-center space-x-2">
        <RadioGroupItem value="RIGHT" id="right" />
        <Label htmlFor="right">Right</Label>
      </div>
    </RadioGroup>
  );
}; 