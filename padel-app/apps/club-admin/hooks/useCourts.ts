import { useQuery } from "@tanstack/react-query";
import { fetchCourts } from "@/lib/api";

export function useCourts(clubId: number) {
  return useQuery({
    queryKey: ["courts", clubId],
    queryFn: () => fetchCourts(clubId),
    enabled: !!clubId,
  });
} 