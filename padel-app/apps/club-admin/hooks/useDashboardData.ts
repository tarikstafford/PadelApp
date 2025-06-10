import { useQuery } from "@tanstack/react-query";
import { fetchDashboardSummary } from "@/lib/api";

export function useDashboardData(clubId: number) {
  const { data, isLoading, error, isFetching, refetch } = useQuery({
    queryKey: ["dashboardSummary", clubId],
    queryFn: () => fetchDashboardSummary(clubId),
    refetchInterval: 60000, // Auto-refresh every minute
    enabled: !!clubId, // Only run the query if clubId is available
  });

  return { data, isLoading, error, isFetching, refetch };
} 