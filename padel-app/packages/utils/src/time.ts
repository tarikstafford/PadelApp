export const formatTime = (timeString: string): string => {
  if (!timeString) return '';
  const [hoursStr, minutesStr] = timeString.split(':');

  if (hoursStr === undefined || minutesStr === undefined) {
    return '';
  }

  const hour = parseInt(hoursStr, 10);
  const minute = parseInt(minutesStr, 10);

  if (isNaN(hour) || isNaN(minute)) {
    return '';
  }

  const ampm = hour >= 12 ? 'PM' : 'AM';
  const formattedHour = hour % 12 || 12; // Convert 0 to 12

  return `${formattedHour}:${minute.toString().padStart(2, '0')} ${ampm}`;
};

export const formatOpeningHours = (openingTime?: string | null, closingTime?: string | null): string => {
  if (!openingTime || !closingTime) {
    return 'Hours not available';
  }
  return `${formatTime(openingTime)} - ${formatTime(closingTime)}`;
}; 