"use client";

import AuthStatus from "../auth/AuthStatus";
import { useAuth } from "@/contexts/AuthContext";
import Link from "next/link";
import { Button } from "@workspace/ui/components/button";
import { usePathname } from "next/navigation";
import LogoutButton from "../auth/LogoutButton";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/courts", label: "Courts" },
  { href: "/bookings", label: "Bookings" },
];

export function DashboardPage({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <DashboardSidebar />
      <div className="flex flex-col flex-1">
        <DashboardHeader />
        <main className="flex-1 p-8">{children}</main>
      </div>
    </div>
  );
}

export function DashboardHeader() {
  return (
    <header className="flex items-center justify-between h-16 px-4 border-b">
      <div>{/* Add any header content here */}</div>
      <div>
        <AuthStatus />
      </div>
    </header>
  );
}

export function DashboardSidebar() {
  const pathname = usePathname();
  const { isAuthenticated } = useAuth();

  return (
    <aside className="w-64 flex-shrink-0 border-r bg-gray-50 p-4 flex flex-col">
      <div className="mb-8">
        <Link href="/dashboard" className="text-2xl font-bold">
          Club Admin
        </Link>
      </div>
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

export function DashboardContent({ children }: { children: React.ReactNode }) {
  return <div className="flex-1 p-8">{children}</div>;
}

export function DashboardNav({ children }: { children: React.ReactNode }) {
    return <nav className="flex-grow">{children}</nav>;
} 