"use client";

import { DashboardPage } from "@/components/layout/Dashboard";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DashboardPage>{children}</DashboardPage>;
} 