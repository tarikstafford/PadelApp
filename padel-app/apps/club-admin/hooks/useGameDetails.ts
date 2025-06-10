import { useQuery } from "@tanstack/react-query";
import { fetchGameDetails } from "@/lib/api";

export function useGameDetails(bookingId: number | null) {
  return useQuery({
    queryKey: ["gameDetails", bookingId],
    queryFn: () => fetchGameDetails(bookingId!),
    enabled: !!bookingId,
  });
} 