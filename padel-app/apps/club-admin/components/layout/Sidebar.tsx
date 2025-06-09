"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@workspace/ui/components/button";
import AuthStatus from "../auth/AuthStatus";
import LogoutButton from "../auth/LogoutButton";
import { useAuth } from "@/contexts/AuthContext";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/courts", label: "Courts" },
  { href: "/bookings", label: "Bookings" },
  { href: "/profile", label: "Profile" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { isAuthenticated } = useAuth();

  return (
    <aside className="w-64 flex-shrink-0 border-r bg-gray-50 p-4 flex flex-col">
      <div className="mb-8">
        <Link href="/dashboard" className="text-2xl font-bold">
          Club Admin
        </Link>
      </div>
      <AuthStatus />
      <nav className="flex-grow">
        <ul className="space-y-2">
          {isAuthenticated && navItems.map((item) => (
            <li key={item.href}>
              <Link href={item.href} legacyBehavior passHref>
                <Button
                  variant={pathname === item.href ? "secondary" : "ghost"}
                  className="w-full justify-start"
                >
                  {item.label}
                </Button>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
      {isAuthenticated && (
        <div className="mt-auto">
          <LogoutButton />
        </div>
      )}
    </aside>
  );
} 