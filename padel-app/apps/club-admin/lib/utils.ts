import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatOpeningHours(openingTime?: string | null, closingTime?: string | null): string {
  const formatTime = (time: string) => {
    const [hours, minutes] = time.split(':');
    if (hours === undefined || minutes === undefined) {
      return "Invalid Time";
    }
    const date = new Date();
    date.setHours(parseInt(hours, 10));
    date.setMinutes(parseInt(minutes, 10));
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  };

  if (openingTime && closingTime) {
    return `${formatTime(openingTime)} - ${formatTime(closingTime)}`;
  }
  
  return "Not specified";
} 