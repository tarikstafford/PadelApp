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
  Skeleton,
  Button,
  Card,
  CardHeader,
  CardTitle
} from "@workspace/ui/components";
import { EloBadge, EloRatingWithBadge, ELO_CATEGORIES } from "@/components/shared/EloBadge";
import { Trophy, Medal, Award, Crown } from "lucide-react";

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
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const limit = 20;

  useEffect(() => {
    const fetchLeaderboard = async () => {
      setLoading(true);
      try {
        const offset = (page - 1) * limit;
        let url = `/leaderboard?limit=${limit}&offset=${offset}`;
        
        // Add category filter if not "all"
        if (selectedCategory !== "all") {
          const category = ELO_CATEGORIES.find(c => c.name.toLowerCase() === selectedCategory);
          if (category) {
            url += `&min_elo=${category.minElo}&max_elo=${category.maxElo}`;
          }
        }
        
        const response = await apiClient.get<LeaderboardResponse>(url);
        setLeaderboard(response);
      } catch (error) {
        console.error("Failed to fetch leaderboard", error);
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, [page, selectedCategory]);

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };
  
  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    setPage(1); // Reset to first page when changing category
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Crown className="h-5 w-5 text-yellow-500" />;
      case 2:
        return <Trophy className="h-5 w-5 text-gray-400" />;
      case 3:
        return <Medal className="h-5 w-5 text-amber-600" />;
      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Player Leaderboard</h1>
        <p className="text-muted-foreground">Compete with players in your skill category</p>
      </div>

      <div className="space-y-6">
        {/* Category Filter Buttons */}
        <div className="flex flex-wrap gap-2 justify-center">
          <Button 
            variant={selectedCategory === "all" ? "default" : "outline"}
            onClick={() => handleCategoryChange("all")}
            className="flex items-center gap-2"
          >
            <Award className="h-4 w-4" />
            All Players
          </Button>
          {ELO_CATEGORIES.map((category) => (
            <Button
              key={category.name.toLowerCase()}
              variant={selectedCategory === category.name.toLowerCase() ? "default" : "outline"}
              onClick={() => handleCategoryChange(category.name.toLowerCase())}
              className="flex items-center gap-2"
            >
              <span>{category.icon}</span>
              {category.name}
            </Button>
          ))}
        </div>

        {/* Category Header */}
        {selectedCategory !== "all" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                {ELO_CATEGORIES.find(c => c.name.toLowerCase() === selectedCategory)?.icon}
                {ELO_CATEGORIES.find(c => c.name.toLowerCase() === selectedCategory)?.name} League
                <EloBadge 
                  eloRating={ELO_CATEGORIES.find(c => c.name.toLowerCase() === selectedCategory)?.minElo || 1.0} 
                  showRange 
                />
              </CardTitle>
            </CardHeader>
          </Card>
        )}

        {/* Leaderboard Content */}
        {loading ? (
          <LeaderboardSkeleton />
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-16">#</TableHead>
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
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">
                          {getRankIcon(rank)}
                          {rank}
                        </div>
                      </TableCell>
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
                      <TableCell className="text-right">
                        <EloRatingWithBadge eloRating={user.elo_rating} size="sm" />
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