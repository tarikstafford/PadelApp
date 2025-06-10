import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchBookings } from "@/lib/api";
import { DateRange } from "react-day-picker";
import { keepPreviousData } from "@tanstack/react-query";

export function useBookings({
  clubId,
  dateRange,
  courtId,
  status,
  search,
  page,
  pageSize,
}: {
  clubId: number;
  dateRange?: DateRange;
  courtId?: string | null;
  status?: string | null;
  search?: string;
  page?: number;
  pageSize?: number;
}) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["bookings", clubId, dateRange, courtId, status, search, page, pageSize],
    queryFn: () =>
      fetchBookings(clubId, {
        start_date: dateRange?.from?.toISOString().split("T")[0],
        end_date: dateRange?.to?.toISOString().split("T")[0],
        court_id: courtId ? Number(courtId) : undefined,
        status: status || undefined,
        search: search || undefined,
        page,
        pageSize,
      }),
    enabled: !!clubId,
    placeholderData: keepPreviousData,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  return { data, isLoading, error };
} 