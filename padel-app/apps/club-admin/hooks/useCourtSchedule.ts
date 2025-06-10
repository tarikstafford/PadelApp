import { useQuery } from "@tanstack/react-query";
import { fetchCourtSchedule } from "@/lib/api";
import { Court, Booking } from "@/lib/types";

export function useCourtSchedule(clubId: number, date: Date | undefined) {
  const dateString = date?.toISOString().split("T")[0];

  return useQuery<{ courts: Court[]; bookings: Booking[] }>({
    queryKey: ["courtSchedule", clubId, dateString],
    queryFn: () => fetchCourtSchedule(clubId, dateString!),
    enabled: !!clubId && !!dateString,
  });
} 