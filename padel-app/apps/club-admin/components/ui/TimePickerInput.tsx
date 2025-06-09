"use client";

import { Input } from "@workspace/ui/components/input";

interface TimePickerInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export function TimePickerInput({ value, onChange, disabled }: TimePickerInputProps) {
  return (
    <Input
      type="time"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
    />
  );
} 