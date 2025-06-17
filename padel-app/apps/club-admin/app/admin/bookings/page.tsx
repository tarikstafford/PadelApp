"use client";

import { useState } from "react";
import { DateRange } from "react-day-picker";
import { useBookings } from "@/hooks/useBookings";
import { DataTable } from "@/components/admin/bookings/data-table";
import { DateRangePicker } from "@workspace/ui/components/date-range-picker";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@workspace/ui/components/select";
import { Input } from "@workspace/ui/components/input";
import { Badge } from "@workspace/ui/components/badge";
import { Button } from "@workspace/ui/components/button";
import { ColumnDef } from "@tanstack/react-table";
import { Booking } from "@/lib/types";
import { BookingDetailsDialog } from "@/components/admin/bookings/booking-details-dialog";

// This would ideally come from an API call
const courts = [
  { id: 1, name: "Court 1" },
  { id: 2, name: "Court 2" },
];

const getStatusVariant = (status: string) => {
  switch (status) {
    case "CONFIRMED":
      return "default";
    case "PENDING":
      return "secondary";
    case "CANCELLED":
      return "destructive";
    default:
      return "outline";
  }
};

export default function BookingsPage() {
  const [dateRange, setDateRange] = useState<DateRange | undefined>({
    from: new Date(),
    to: new Date(new Date().setDate(new Date().getDate() + 7)),
  });
  const [courtFilter, setCourtFilter] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 });
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const clubId = 1; // Hardcoded for now
  const { data, isLoading, error } = useBookings({
    clubId,
    dateRange,
    courtId: courtFilter,
    status: statusFilter,
    search: searchQuery,
    page: pagination.pageIndex + 1,
    pageSize: pagination.pageSize,
  });

  const handleViewBooking = (booking: Booking) => {
    setSelectedBooking(booking);
    setIsDialogOpen(true);
  };

  const columns: ColumnDef<Booking>[] = [
    {
      accessorKey: "id",
      header: "ID",
    },
    {
      accessorKey: "start_time",
      header: "Date",
      cell: ({ row }) =>
        new Date(row.getValue("start_time")).toLocaleDateString(),
    },
    {
      accessorKey: "start_time",
      header: "Time",
      cell: ({ row }) => {
        const booking = row.original;
        return `${new Date(booking.start_time).toLocaleTimeString()} - ${new Date(
          booking.end_time
        ).toLocaleTimeString()}`;
      },
    },
    {
      accessorKey: "court.name",
      header: "Court",
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <Badge variant={getStatusVariant(row.getValue("status"))}>
          {row.getValue("status")}
        </Badge>
      ),
    },
    {
      id: "actions",
      cell: ({ row }) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => handleViewBooking(row.original)}
        >
          View
        </Button>
      ),
    },
  ];

  const handleDateRangeSelect = (newDateRange?: DateRange) => {
    setDateRange(newDateRange);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Bookings</h1>
      <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
        <DateRangePicker date={dateRange} onDateChange={handleDateRangeSelect} />
        <div className="flex gap-2">
          <Select
            value={courtFilter || ""}
            onValueChange={(value) => setCourtFilter(value || null)}
          >
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="All Courts" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Courts</SelectItem>
              {courts.map((court) => (
                <SelectItem key={court.id} value={String(court.id)}>
                  {court.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={statusFilter || ""}
            onValueChange={(value) => setStatusFilter(value || null)}
            data-testid="status-filter"
          >
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Statuses</SelectItem>
              <SelectItem value="CONFIRMED">Confirmed</SelectItem>
              <SelectItem value="PENDING">Pending</SelectItem>
              <SelectItem value="CANCELLED">Cancelled</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex-1">
          <Input
            placeholder="Search bookings..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full"
          />
        </div>
      </div>
      <DataTable
        columns={columns}
        data={data || []}
        pageCount={-1}
        pagination={pagination}
        setPagination={setPagination}
        isLoading={isLoading}
        error={error}
      />
      <BookingDetailsDialog
        booking={selectedBooking}
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
      />
    </div>
  );
} 