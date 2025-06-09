"use client";

import { useState } from "react";
import { Checkbox } from "@workspace/ui/components/checkbox";
import { Label } from "@workspace/ui/components/label";
import { TimePickerInput } from "../ui/TimePickerInput";

interface DayHours {
  open: string;
  close: string;
}

interface OperationalHours {
  monday: DayHours | null;
  tuesday: DayHours | null;
  wednesday: DayHours | null;
  thursday: DayHours | null;
  friday: DayHours | null;
  saturday: DayHours | null;
  sunday: DayHours | null;
}

interface OperationalHoursProps {
  value: OperationalHours;
  onChange: (hours: OperationalHours) => void;
}

export function OperationalHoursSelector({ value, onChange }: OperationalHoursProps) {
  const [selectedDays, setSelectedDays] = useState<Record<string, boolean>>({
    monday: !!value.monday,
    tuesday: !!value.tuesday,
    wednesday: !!value.wednesday,
    thursday: !!value.thursday,
    friday: !!value.friday,
    saturday: !!value.saturday,
    sunday: !!value.sunday,
  });

  const handleDayToggle = (day: keyof OperationalHours) => {
    const newSelectedDays = { ...selectedDays, [day]: !selectedDays[day] };
    setSelectedDays(newSelectedDays);
    
    if (!newSelectedDays[day]) {
      onChange({ ...value, [day]: null });
    } else if (!value[day]) {
      onChange({ ...value, [day]: { open: "09:00", close: "17:00" } });
    }
  };

  const handleHoursChange = (day: keyof OperationalHours, field: 'open' | 'close', time: string) => {
    if (!value[day]) return;
    onChange({
      ...value,
      [day]: { ...value[day], [field]: time }
    });
  };

  const renderDayRow = (day: keyof OperationalHours, label: string) => (
    <div className="flex items-center space-x-4 mb-4">
      <Checkbox 
        id={`${day}-active`} 
        checked={selectedDays[day]} 
        onCheckedChange={() => handleDayToggle(day)}
      />
      <Label htmlFor={`${day}-active`} className="w-24">{label}</Label>
      
      {selectedDays[day] && (
        <div className="flex items-center space-x-2">
          <TimePickerInput
            value={value[day]?.open || "09:00"}
            onChange={(time) => handleHoursChange(day, 'open', time)}
            disabled={!selectedDays[day]}
          />
          <span>to</span>
          <TimePickerInput
            value={value[day]?.close || "17:00"}
            onChange={(time) => handleHoursChange(day, 'close', time)}
            disabled={!selectedDays[day]}
          />
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium">Operational Hours</h3>
      <div className="space-y-2">
        {renderDayRow("monday", "Monday")}
        {renderDayRow("tuesday", "Tuesday")}
        {renderDayRow("wednesday", "Wednesday")}
        {renderDayRow("thursday", "Thursday")}
        {renderDayRow("friday", "Friday")}
        {renderDayRow("saturday", "Saturday")}
        {renderDayRow("sunday", "Sunday")}
      </div>
    </div>
  );
} 