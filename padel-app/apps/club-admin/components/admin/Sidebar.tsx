"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Calendar, Users, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { name: "Dashboard", href: "/admin", icon: Home },
  { name: "Bookings", href: "/admin/bookings", icon: Calendar },
  { name: "Schedule", href: "/admin/schedule", icon: Calendar },
  { name: "Club Profile", href: "/admin/club", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="w-64 bg-background border-r h-full">
      <div className="p-4">
        <h2 className="text-xl font-bold">PadelGo Admin</h2>
      </div>
      <nav className="space-y-1 px-2">
        {navItems.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              "flex items-center px-4 py-2 text-sm rounded-md",
              pathname === item.href
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-muted"
            )}
          >
            <item.icon className="mr-3 h-4 w-4" />
            {item.name}
          </Link>
        ))}
      </nav>
    </div>
  );
} 