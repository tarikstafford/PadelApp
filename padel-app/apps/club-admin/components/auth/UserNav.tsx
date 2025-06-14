"use client";

import { useAuth } from "@/contexts/AuthContext";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@workspace/ui/components/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@workspace/ui/components/avatar";
import { Button } from "@workspace/ui/components/button";
import { Loader2 } from "lucide-react";
import Link from "next/link";

export function UserNav() {
  const { user, logout, isLoading } = useAuth();

  if (isLoading) {
    return <Loader2 className="h-5 w-5 animate-spin" />;
  }

  if (!user) {
    return (
      <Link href="/login" passHref>
        <Button variant="ghost">Login</Button>
      </Link>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger>
        <Avatar className="h-9 w-9">
          <AvatarImage src={user.profile_picture_url || ""} alt={user.full_name || "User"} />
          <AvatarFallback>{user.full_name?.charAt(0).toUpperCase() || "U"}</AvatarFallback>
        </Avatar>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">{user.full_name}</p>
            <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem disabled>Profile</DropdownMenuItem>
        <DropdownMenuItem disabled>Settings</DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={logout}>
          Logout
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
} 