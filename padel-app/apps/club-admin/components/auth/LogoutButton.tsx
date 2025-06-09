"use client";

import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@workspace/ui/components/button";
import { LogOut } from "lucide-react";

export default function LogoutButton() {
  const { logout } = useAuth();

  return (
    <Button variant="ghost" className="w-full justify-start" onClick={logout}>
      <LogOut className="mr-2 h-4 w-4" />
      Logout
    </Button>
  );
} 