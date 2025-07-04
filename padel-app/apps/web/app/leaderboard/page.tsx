"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api";
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
  Skeleton
} from "@workspace/ui/components";

interface LeaderboardUser {
  id: number;
  full_name: string;
  avatar_url: string | null;
  club_name: string | null;
  elo_rating: number;
}

interface LeaderboardResponse {
  total: number;
  offset: number;
  limit: number;
  users: LeaderboardUser[];
}

const LeaderboardPage = () => {
  const [loading, setLoading] = useState(true);
  const [leaderboard, setLeaderboard] = useState<LeaderboardResponse | null>(
    null
  );
  const [page, setPage] = useState(1);
  const limit = 20;

  useEffect(() => {
    const fetchLeaderboard = async () => {
      setLoading(true);
      try {
        const offset = (page - 1) * limit;
        const response = await apiClient.get<LeaderboardResponse>(
          `/leaderboard?limit=${limit}&offset=${offset}`
        );
        setLeaderboard(response);
      } catch (error) {
        console.error("Failed to fetch leaderboard", error);
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, [page]);

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">Player Leaderboard</h1>

      {loading ? (
        <LeaderboardSkeleton />
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">#</TableHead>
                <TableHead>Player</TableHead>
                <TableHead>Club</TableHead>
                <TableHead className="text-right">Rating</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {leaderboard?.users && leaderboard.users.map((user, index) => {
                const rank = (page - 1) * limit + index + 1;
                return (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">{rank}</TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <Avatar>
                          <AvatarImage src={user.avatar_url || undefined} />
                          <AvatarFallback>{user.full_name.substring(0, 2)}</AvatarFallback>
                        </Avatar>
                        <span>{user.full_name}</span>
                      </div>
                    </TableCell>
                    <TableCell>{user.club_name || "-"}</TableCell>
                    <TableCell className="text-right font-bold">
                      {user.elo_rating.toFixed(1)}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>

          {leaderboard && (
            <div className="mt-4 flex justify-center">
              <Pagination>
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious
                      href="#"
                      onClick={() => handlePageChange(page - 1)}
                      className={page === 1 ? "pointer-events-none opacity-50" : ""}
                      size="icon"
                    />
                  </PaginationItem>
                  {[...Array(Math.ceil(leaderboard.total / limit))].map((_, i) => (
                    <PaginationItem key={i}>
                      <PaginationLink
                        href="#"
                        onClick={() => handlePageChange(i + 1)}
                        isActive={page === i + 1}
                        size="icon"
                      >
                        {i + 1}
                      </PaginationLink>
                    </PaginationItem>
                  ))}
                  <PaginationItem>
                    <PaginationNext
                      href="#"
                      onClick={() => handlePageChange(page + 1)}
                      className={page === Math.ceil(leaderboard.total / limit) ? "pointer-events-none opacity-50" : ""}
                      size="icon"
                    />
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            </div>
          )}
        </>
      )}
    </div>
  );
};

const LeaderboardSkeleton = () => (
  <div className="space-y-4">
    <Skeleton className="h-8 w-1/4" />
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-12">
            <Skeleton className="h-6 w-full" />
          </TableHead>
          <TableHead>
            <Skeleton className="h-6 w-full" />
          </TableHead>
          <TableHead>
            <Skeleton className="h-6 w-full" />
          </TableHead>
          <TableHead>
            <Skeleton className="h-6 w-full" />
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[...Array(10)].map((_, i) => (
          <TableRow key={i}>
            <TableCell>
              <Skeleton className="h-6 w-full" />
            </TableCell>
            <TableCell>
              <div className="flex items-center space-x-3">
                <Skeleton className="h-10 w-10 rounded-full" />
                <Skeleton className="h-6 w-32" />
              </div>
            </TableCell>
            <TableCell>
              <Skeleton className="h-6 w-24" />
            </TableCell>
            <TableCell>
              <Skeleton className="h-6 w-16 ml-auto" />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  </div>
);

export default LeaderboardPage; 