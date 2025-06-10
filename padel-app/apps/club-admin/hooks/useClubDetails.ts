import { useQuery } from "@tanstack/react-query";
import { fetchClubDetails } from "@/lib/api";

export function useClubDetails(clubId: number | null) {
  return useQuery({
    queryKey: ["clubDetails", clubId],
    queryFn: () => fetchClubDetails(clubId!),
    enabled: !!clubId,
  });
} 